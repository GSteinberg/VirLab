//***************************************************************************
//* Copyright (c) 2015 Saint Petersburg State University
//* Copyright (c) 2011-2014 Saint Petersburg Academic University
//* All Rights Reserved
//* See file LICENSE for details.
//***************************************************************************

#include "modules/alignment/pacbio/pac_index.hpp"
#include "hybrid_gap_closer.hpp"
#include "modules/alignment/long_read_mapper.hpp"
#include "io/reads/wrapper_collection.hpp"
#include "assembly_graph/stats/picture_dump.hpp"
#include "hybrid_aligning.hpp"
#include "pair_info_count.hpp"
#include "io/reads/multifile_reader.hpp"

namespace debruijn_graph {

namespace gap_closing {

//TODO standard aligner badly needs spurious match filtering
class GapTrackingListener : public SequenceMapperListener {
    const Graph& g_;
    GapStorage& gap_storage_;
    const GapStorage empty_storage_;
    std::vector<GapStorage> buffer_storages_;

    const GapDescription INVALID_GAP;

    template<class ReadT>
    std::vector<GapDescription> InferGaps(const ReadT& read,
                                          const MappingPath<EdgeId>& mapping) const {
        TerminalVertexCondition<Graph> tip_condition(g_);
        DEBUG("Inferring gaps")
        VERIFY(!mapping.empty());
        std::vector<GapDescription> answer;
        for (size_t i = 0; i < mapping.size() - 1; ++i) {
            EdgeId e1 = mapping.edge_at(i);
            EdgeId e2 = mapping.edge_at(i + 1);

            //sorry, loops and other special cases
            if (e1 != e2 && e1 != g_.conjugate(e2)
                && e1 != g_.conjugate(e1) && e2 != g_.conjugate(e2)
                && tip_condition.Check(g_.EdgeEnd(e1))
                && tip_condition.Check(g_.EdgeStart(e2))) {

                MappingRange mr1 = mapping.mapping_at(i);
                MappingRange mr2 = mapping.mapping_at(i + 1);
                DEBUG("Creating description from mapping ranges " << mr1 << " and " << mr2);
                size_t seq_start = mr1.initial_range.end_pos + g_.k();
                size_t seq_end = mr2.initial_range.start_pos;

                auto gap = CreateGapInfoTryFixOverlap(g_, read, seq_start, seq_end,
                                                      e1, mr1.mapped_range.end_pos,
                                                      e2, mr2.mapped_range.start_pos);

                if (gap != INVALID_GAP) {
                    answer.push_back(gap);
                }
            }
        }
        return answer;
    }

    template<class ReadT>
    void InnerProcessRead(size_t thread_index, const ReadT& read, const MappingPath<EdgeId>& mapping) {
        DEBUG("Processing read");
        if (!mapping.empty()) {
            for (const auto& gap: InferGaps(read, mapping)) {
                DEBUG("Adding gap info " << gap.str(g_));
                buffer_storages_[thread_index].AddGap(gap);
            }
        } else {
            DEBUG("Mapping was empty");
        }
        DEBUG("Read processed");
    }

public:

    //ALERT passed path_storage should be empty!
    GapTrackingListener(const Graph& g,
                        GapStorage& gap_storage) :
            g_(g), gap_storage_(gap_storage), empty_storage_(gap_storage) {
        VERIFY(empty_storage_.size() == 0);
    }

    void StartProcessLibrary(size_t threads_count) override {
        for (size_t i = 0; i < threads_count; ++i) {
            buffer_storages_.push_back(empty_storage_);
        }
    }

    void StopProcessLibrary() override {
        //FIXME put this code into ancestor
        for (size_t i = 0; i < buffer_storages_.size(); ++i) {
            MergeBuffer(i);
        }
        buffer_storages_.clear();
    }

    void MergeBuffer(size_t thread_index) override {
        DEBUG("Merge buffer " << thread_index << " with size " << buffer_storages_[thread_index].size());
        gap_storage_.AddStorage(buffer_storages_[thread_index]);
        buffer_storages_[thread_index].clear();
        DEBUG("Now size " << gap_storage_.size());
    }

    void ProcessSingleRead(size_t thread_index,
                           const io::SingleRead& read,
                           const MappingPath<EdgeId>& mapping) override {
        InnerProcessRead(thread_index, read, mapping);
    }

    void ProcessSingleRead(size_t thread_index,
                           const io::SingleReadSeq& read,
                           const MappingPath<EdgeId>& mapping) override {
        InnerProcessRead(thread_index, read, mapping);
    }

    void ProcessPairedRead(size_t,
                           const io::PairedReadSeq&,
                           const MappingPath<EdgeId>&,
                           const MappingPath<EdgeId>&) override {
        //nothing to do
    }

    void ProcessPairedRead(size_t,
                           const io::PairedRead&,
                           const MappingPath<EdgeId>&,
                           const MappingPath<EdgeId>&) override {
        //nothing to do
    }

private:
    DECL_LOGGER("GapTrackingListener");
};

void CloseGaps(conj_graph_pack& gp, bool rtype,
               const GapStorage& gap_storage,
               size_t min_weight) {
    INFO("Closing gaps with long reads");

    HybridGapCloser::ConsensusF consensus_f;
    if (rtype) {
        consensus_f = &PoaConsensus;
    } else {
        consensus_f = [=](const std::vector<string>& gap_seqs) {
            return TrivialConsenus(gap_seqs, cfg::get().pb.max_contigs_gap_length);
        };
    }

    HybridGapCloser gap_closer(gp.g, gap_storage,
                               min_weight, consensus_f,
                               cfg::get().pb.long_seq_limit);
    auto replacement = gap_closer();

    for (size_t j = 0; j < cfg::get().ds.reads.lib_count(); j++) {
        gp.single_long_reads[j].ReplaceEdges(replacement);
    }

    INFO("Closing gaps with long reads finished");
}
}

bool IsNontrivialAlignment(const std::vector<std::vector<EdgeId>>& aligned_edges) {
    for (size_t j = 0; j < aligned_edges.size(); j++)
        if (aligned_edges[j].size() > 1)
            return true;
    return false;
}

io::SingleStreamPtr GetReadsStream(const io::SequencingLibrary<config::LibraryData>& lib) {
    io::ReadStreamList<io::SingleRead> streams;
    for (const auto& reads : lib.single_reads())
        //do we need input_file function here?
        //TODO add decent support for N-s?
        streams.push_back(make_shared<io::FixingWrapper>(make_shared<io::FileReadStream>(reads)));
    return io::MultifileWrap(streams);
}

class PacbioAligner {
    const pacbio::PacBioMappingIndex<Graph>& pac_index_;
    PathStorage<Graph>& path_storage_;
    gap_closing::GapStorage& gap_storage_;
    pacbio::StatsCounter stats_;
    const PathStorage<Graph> empty_path_storage_;
    const gap_closing::GapStorage empty_gap_storage_;
    const size_t read_buffer_size_;

    void ProcessReadsBatch(const std::vector<io::SingleRead>& reads, size_t thread_cnt) {
        std::vector<PathStorage<Graph>> long_reads_by_thread(thread_cnt,
                                                             empty_path_storage_);
        std::vector<gap_closing::GapStorage> gaps_by_thread(thread_cnt,
                                                            empty_gap_storage_);
        std::vector<pacbio::StatsCounter> stats_by_thread(thread_cnt);

        size_t longer_500 = 0;
        size_t aligned = 0;
        size_t nontrivial_aligned = 0;

        #pragma omp parallel for reduction(+: longer_500, aligned, nontrivial_aligned)
        for (size_t i = 0; i < reads.size(); ++i) {
            size_t thread_num = omp_get_thread_num();
            DEBUG(reads[i].name());
            auto current_read_mapping = pac_index_.GetReadAlignment(reads[i]);
            for (const auto& gap : current_read_mapping.gaps) {
                gaps_by_thread[thread_num].AddGap(gap);
            }

            const auto& aligned_edges = current_read_mapping.main_storage;
            for (const auto& path : aligned_edges)
                long_reads_by_thread[thread_num].AddPath(path, 1, true);

            //counting stats:
            for (const auto& path : aligned_edges)
                stats_by_thread[thread_num].path_len_in_edges[path.size()]++;

            if (reads[i].size() > 500) {
                longer_500++;
                if (aligned_edges.size() > 0) {
                    aligned++;
                    if (IsNontrivialAlignment(aligned_edges)) {
                        nontrivial_aligned++;
                    }
                }
            }
        }

        INFO("Read batch of size: " << reads.size() << " processed; "
                                    << longer_500 << " of them longer than 500; among long reads aligned: "
                                    << aligned << "; paths of more than one edge received: "
                                    << nontrivial_aligned);

        for (size_t i = 0; i < thread_cnt; i++) {
            path_storage_.AddStorage(long_reads_by_thread[i]);
            gap_storage_.AddStorage(gaps_by_thread[i]);
            stats_.AddStorage(stats_by_thread[i]);
        }
    }

public:
    PacbioAligner(const pacbio::PacBioMappingIndex<Graph>& pac_index,
                  PathStorage<Graph>& path_storage,
                  gap_closing::GapStorage& gap_storage,
                  size_t read_buffer_size = 50000) :
            pac_index_(pac_index),
            path_storage_(path_storage),
            gap_storage_(gap_storage),
            empty_path_storage_(path_storage),
            empty_gap_storage_(gap_storage),
            read_buffer_size_(read_buffer_size) {
        VERIFY(empty_path_storage_.size() == 0);
        VERIFY(empty_gap_storage_.size() == 0);
    }

    void operator()(io::SingleStream& read_stream, size_t thread_cnt) {
        size_t n = 0;
        size_t buffer_no = 0;
        while (!read_stream.eof()) {
            std::vector<io::SingleRead> read_buffer;
            read_buffer.reserve(read_buffer_size_);
            io::SingleRead read;
            for (size_t buf_size = 0; buf_size < read_buffer_size_ && !read_stream.eof(); ++buf_size) {
                read_stream >> read;
                read_buffer.push_back(std::move(read));
            }
            INFO("Prepared batch " << buffer_no << " of " << read_buffer.size() << " reads.");
            DEBUG("master thread number " << omp_get_thread_num());
            ProcessReadsBatch(read_buffer, thread_cnt);
            ++buffer_no;
            n += read_buffer.size();
            INFO("Processed " << n << " reads");
        }
    }

    const pacbio::StatsCounter& stats() const {
        return stats_;
    }
};

void PacbioAlignLibrary(const conj_graph_pack& gp,
                        const io::SequencingLibrary<config::LibraryData>& lib,
                        PathStorage<Graph>& path_storage,
                        gap_closing::GapStorage& gap_storage,
                        size_t thread_cnt, const config::pacbio_processor &pb) {
    string lib_for_info = (lib.is_long_read_lib() ? "long reads" : "contigs");
    INFO("Aligning "<< lib_for_info << " with bwa-mem based aligner");

    alignment::BWAIndex::AlignmentMode mode =
            (lib.type() == io::LibraryType::PacBioReads ?
             alignment::BWAIndex::AlignmentMode::PacBio : alignment::BWAIndex::AlignmentMode::Ont2D);

    // Initialize index
    pacbio::PacBioMappingIndex<Graph> pac_index(gp.g, pb,
                                                mode);

    PacbioAligner aligner(pac_index, path_storage, gap_storage);

    auto stream = GetReadsStream(lib);
    aligner(*stream, thread_cnt);

    INFO("For library of " << lib_for_info);
    aligner.stats().Report();
    INFO("Aligning of " << lib_for_info <<" finished");
}

bool ShouldAlignWithPacbioAligner(io::LibraryType lib_type) {
    return lib_type == io::LibraryType::UntrustedContigs ||
           lib_type == io::LibraryType::PacBioReads ||
           lib_type == io::LibraryType::SangerReads ||
           lib_type == io::LibraryType::NanoporeReads; //||
//           lib_type == io::LibraryType::TSLReads;
}

void HybridLibrariesAligning::run(conj_graph_pack& gp, const char*) {
    using namespace omnigraph;

    bool make_additional_saves = parent_->saves_policy().make_saves_;
    for (size_t lib_id = 0; lib_id < cfg::get().ds.reads.lib_count(); ++lib_id) {
        if (cfg::get().ds.reads[lib_id].is_hybrid_lib()) {
            INFO("Hybrid library detected: #" << lib_id);

            const auto& lib = cfg::get().ds.reads[lib_id];
            bool rtype = lib.is_long_read_lib();

            auto& path_storage = gp.single_long_reads[lib_id];
            gap_closing::GapStorage gap_storage(gp.g);

            if (ShouldAlignWithPacbioAligner(lib.type())) {
                //TODO put alternative alignment right here
                PacbioAlignLibrary(gp, lib,
                                   path_storage, gap_storage,
                                   cfg::get().max_threads, cfg::get().pb);
            } else {
                gp.EnsureBasicMapping();
                gap_closing::GapTrackingListener mapping_listener(gp.g, gap_storage);
                INFO("Processing reads from hybrid library " << lib_id);

                //FIXME make const
                auto& reads = cfg::get_writable().ds.reads[lib_id];

                SequenceMapperNotifier notifier(gp, cfg::get_writable().ds.reads.lib_count());
                //FIXME pretty awful, would be much better if listeners were shared ptrs
                LongReadMapper read_mapper(gp.g, gp.single_long_reads[lib_id],
                                           ChooseProperReadPathExtractor(gp.g, reads.type()));

                notifier.Subscribe(lib_id, &mapping_listener);
                notifier.Subscribe(lib_id, &read_mapper);

                //TODO think of N's proper handling
                // (currently handled by BasicSequenceMapper and concatenated in single MappingPath)
                auto single_streams = single_easy_readers(reads, false,
                                                          /*map_paired*/false, /*handle Ns*/false);

                notifier.ProcessLibrary(single_streams, lib_id, *MapperInstance(gp));
                cfg::get_writable().ds.reads[lib_id].data().single_reads_mapped = true;

                INFO("Finished processing long reads from lib " << lib_id);
                gp.index.Detach();
            }

            if (make_additional_saves) {
                INFO("Producing additional saves");
                path_storage.DumpToFile(cfg::get().output_saves + "long_reads_before_rep.mpr",
                                        map<EdgeId, EdgeId>(), /*min_stats_cutoff*/rtype ? 1 : 0, true);
                gap_storage.DumpToFile(cfg::get().output_saves + "gaps.mpr");
            }

            INFO("Padding gaps");
            size_t min_gap_quantity = rtype ? cfg::get().pb.pacbio_min_gap_quantity
                                            : cfg::get().pb.contigs_min_gap_quantity;

            INFO("Min gap weight set to " << min_gap_quantity);
            gap_storage.PrepareGapsForClosure(min_gap_quantity, /*max flank length*/500);

            gap_closing::CloseGaps(gp, rtype, gap_storage, min_gap_quantity);
        }
    }

    visualization::graph_labeler::DefaultLabeler<Graph> labeler(gp.g, gp.edge_pos);
    stats::detail_info_printer printer(gp, labeler, cfg::get().output_dir);
    printer(config::info_printer_pos::final_gap_closed);
}

}
