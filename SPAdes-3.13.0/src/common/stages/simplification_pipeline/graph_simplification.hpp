//***************************************************************************
//* Copyright (c) 2015 Saint Petersburg State University
//* Copyright (c) 2011-2014 Saint Petersburg Academic University
//* All Rights Reserved
//* See file LICENSE for details.
//***************************************************************************

/*
 * graph_simplification.hpp
 *
 *  Created on: Aug 12, 2011
 *      Author: sergey
 */

#pragma once

#include "pipeline/config_struct.hpp"

#include "modules/simplification/tip_clipper.hpp"
#include "modules/simplification/complex_tip_clipper.hpp"
#include "modules/simplification/bulge_remover.hpp"
#include "modules/simplification/complex_bulge_remover.hpp"
#include "modules/simplification/erroneous_connection_remover.hpp"
#include "modules/simplification/relative_coverage_remover.hpp"
#include "modules/simplification/mf_ec_remover.hpp"
#include "modules/simplification/parallel_simplification_algorithms.hpp"
#include "stages/simplification_pipeline/simplification_settings.hpp"

#include "modules/graph_read_correction.hpp"

#include "assembly_graph/graph_support/chimera_stats.hpp"
#include "assembly_graph/graph_support/basic_edge_conditions.hpp"
#include "assembly_graph/stats/picture_dump.hpp"
#include "assembly_graph/graph_support/parallel_processing.hpp"
#include "assembly_graph/graph_support/detail_coverage.hpp"

#include "assembly_graph/core/graph.hpp"

#include "visualization/graph_colorer.hpp"
#include "utils/standard_base.hpp"

namespace debruijn {

namespace simplification {

//todo remove this line
using namespace debruijn_graph;

template<class Graph>
class ConditionParser {
private:
    typedef typename Graph::EdgeId EdgeId;

    const Graph &g_;
    string next_token_;
    string input_;
    const SimplifInfoContainer settings_;
    /*(curr_iter + 1) / total_iter*/
    double iter_run_progress_;
    std::queue<string> tokenized_input_;

    size_t max_length_bound_;
    double max_coverage_bound_;
    int requested_iterations_;

    string ReadNext() {
        if (!tokenized_input_.empty()) {
            next_token_ = tokenized_input_.front();
            tokenized_input_.pop();
        } else {
            next_token_ = "";
        }
        return next_token_;
    }

    template<typename T>
    bool RelaxMax(T &cur_max, T t) {
        if (t > cur_max) {
            cur_max = t;
            return true;
        }
        return false;
    }

    template<typename T>
    bool RelaxMin(T &cur_min, T t) {
        if (t < cur_min) {
            cur_min = t;
            return true;
        }
        return false;
    }

    double GetCoverageBound() {
        if (next_token_ == "auto") {
            return settings_.detected_coverage_bound();
        } else {
            return std::stod(next_token_);
        }
    }

    func::TypedPredicate<EdgeId> ParseCondition(size_t &min_length_bound,
                                               double &min_coverage_bound) {
        if (next_token_ == "tc_lb") {
            double length_coeff = std::stod(ReadNext());

            DEBUG("Creating tip length bound. Coeff " << length_coeff);
            size_t length_bound = LengthThresholdFinder::MaxTipLength(
                settings_.read_length(), g_.k(), length_coeff);

            DEBUG("Length bound " << length_bound);

            RelaxMin(min_length_bound, length_bound);
            DEBUG("Min length bound - " << min_length_bound);
            return LengthUpperBound<Graph>(g_, length_bound);

        } else if (next_token_ == "rlmk") {
            //Read length minus k
            VERIFY_MSG(settings_.read_length() > g_.k(), "Read length was shorter than K");
            double length_coeff = std::stod(ReadNext());
            DEBUG("Creating (rl - k) bound. Multiplicative coefficient: " << length_coeff);
            size_t length_bound = size_t(math::round(length_coeff * double(settings_.read_length() - g_.k())));
            RelaxMin(min_length_bound, length_bound);
            DEBUG("Min length bound - " << min_length_bound);
            return LengthUpperBound<Graph>(g_, length_bound);
        } else if (next_token_ == "rl") {
            //Read length
            VERIFY_MSG(settings_.read_length() > 0, "Read was zero");
            double length_coeff = std::stod(ReadNext());
            DEBUG("Creating rl bound. Multiplicative coefficient: " << length_coeff);
            size_t length_bound = size_t(math::round(length_coeff * double(settings_.read_length())));
            RelaxMin(min_length_bound, length_bound);
            DEBUG("Min length bound - " << min_length_bound);
            return LengthUpperBound<Graph>(g_, length_bound);
        } else if (next_token_ == "to_ec_lb") {
            double length_coeff = std::stod(ReadNext());

            DEBUG( "Creating length bound for erroneous connections originated from tip merging. Coeff " << length_coeff);
            size_t length_bound =
                    LengthThresholdFinder::MaxTipOriginatedECLength(
                        settings_.read_length(), g_.k(), length_coeff);

            DEBUG("Length bound " << length_bound);

            RelaxMin(min_length_bound, length_bound);
            DEBUG("Min length bound - " << min_length_bound);
            return LengthUpperBound<Graph>(g_, length_bound);

        } else if (next_token_ == "ec_lb") {
            size_t length_coeff = std::stoll(ReadNext());

            DEBUG("Creating ec length bound. Coeff " << length_coeff);
            size_t length_bound =
                    LengthThresholdFinder::MaxErroneousConnectionLength(
                        g_.k(), length_coeff);

            DEBUG("Length bound " << length_bound);

            RelaxMin(min_length_bound, length_bound);
            DEBUG("Min length bound - " << min_length_bound);
            return LengthUpperBound<Graph>(g_, length_bound);
        } else if (next_token_ == "lb") {
            size_t length_bound = std::stoll(ReadNext());

            DEBUG("Creating length bound. Value " << length_bound);

            RelaxMin(min_length_bound, length_bound);
            DEBUG("Min length bound - " << min_length_bound);
            return LengthUpperBound<Graph>(g_, length_bound);
        } else if (next_token_ == "cb") {
            ReadNext();
            double cov_bound = GetCoverageBound();
            DEBUG("Creating coverage upper bound " << cov_bound);
            RelaxMin(min_coverage_bound, cov_bound);
            return CoverageUpperBound<Graph>(g_, cov_bound);
        } else if (next_token_ == "icb") {
            ReadNext();
            double cov_bound = GetCoverageBound();
            cov_bound = cov_bound * iter_run_progress_;
            DEBUG("Creating iterative coverage upper bound " << cov_bound);
            RelaxMin(min_coverage_bound, cov_bound);
            return CoverageUpperBound<Graph>(g_, cov_bound);
        } else if (next_token_ == "nbr") {
            return NotBulgeECCondition<Graph>(g_);
        } else if (next_token_ == "rctc") {
            ReadNext();
            DEBUG("Creating relative cov tip cond " << next_token_);
            return RelativeCoverageTipCondition<Graph>(g_, std::stod(next_token_));
        } else if (next_token_ == "disabled") {
            DEBUG("Creating disabling condition");
            return func::AlwaysFalse<EdgeId>();
        } else if (next_token_ == "mmm") {
            ReadNext();
            DEBUG("Creating max mismatches cond " << next_token_);
            return MismatchTipCondition<Graph>(g_, std::stod(next_token_));
        } else {
            VERIFY(false);
            return func::AlwaysTrue<EdgeId>();
        }
    }

    func::TypedPredicate<EdgeId> ParseConjunction(size_t &min_length_bound,
                                                  double &min_coverage_bound) {
        func::TypedPredicate<EdgeId> answer = func::AlwaysTrue<EdgeId>();
        VERIFY(next_token_ == "{");
        ReadNext();
        while (next_token_ != "}") {
            answer = func::And(answer,
                              ParseCondition(min_length_bound, min_coverage_bound));
            ReadNext();
        }
        return answer;
    }

public:

    ConditionParser(const Graph &g, string input, const SimplifInfoContainer &settings,
                    double iter_run_progress = 1.)
                    //size_t curr_iteration = 0, size_t iteration_cnt = 1)
            : g_(g),
              input_(input),
              settings_(settings),
              iter_run_progress_(iter_run_progress),
              //iter_run_progress_((double) (curr_iteration + 1) / (double) iteration_cnt),
              max_length_bound_(0),
              max_coverage_bound_(0.),
              requested_iterations_(1) {
        DEBUG("Creating parser for string " << input);
        using namespace boost;
        vector<string> tmp_tokenized_input;
        boost::split(tmp_tokenized_input, input_, boost::is_any_of(" ,;"), boost::token_compress_on);
        for (const auto &s : tmp_tokenized_input) {
            tokenized_input_.push(s);
        }
        ReadNext();
    }

    func::TypedPredicate<EdgeId> operator()() {
        DEBUG("Parsing");
        func::TypedPredicate<EdgeId> answer = func::AlwaysFalse<EdgeId>();
        if (next_token_ == "loop") {
            requested_iterations_ = std::stoi(ReadNext());
            ReadNext();
        }

        VERIFY_MSG(next_token_ == "{", "Expected \"{\", but next token was " << next_token_);
        while (next_token_ == "{") {
            size_t min_length_bound = numeric_limits<size_t>::max();
            double min_coverage_bound = numeric_limits<double>::max();
            answer = func::Or(answer,
                             ParseConjunction(min_length_bound, min_coverage_bound));
            RelaxMax(max_length_bound_, min_length_bound);
            RelaxMax(max_coverage_bound_, min_coverage_bound);
            ReadNext();
        }
        return answer;
    }

    size_t max_length_bound() const {
        return max_length_bound_;
    }

    double max_coverage_bound() const {
        return max_coverage_bound_;
    }

    int requested_iterations() const {
        return requested_iterations_;
    }

private:
    DECL_LOGGER("ConditionParser");
};

template<class Graph>
class EditDistanceTrackingCallback {
    typedef typename Graph::EdgeId EdgeId;
    const Graph &g_;

public:
    EditDistanceTrackingCallback(const Graph &g)
            : g_(g) {
    }

    bool operator()(EdgeId edge, const vector<EdgeId>& path) const {
        Sequence path_sequence = MergeSequences(g_, path);
        size_t dist = EditDistance(g_.EdgeNucls(edge), path_sequence);
        TRACE( "Bulge sequences with distance " << dist << " were " << g_.EdgeNucls(edge) << " and " << path_sequence);
        return true;
    }

private:
    DECL_LOGGER("EditDistanceTrackingCallback");
};

//enabling tip projection
template<class gp_t>
EdgeRemovalHandlerF<typename gp_t::graph_t> WrapWithProjectionCallback(
    gp_t &gp,
    EdgeRemovalHandlerF<typename gp_t::graph_t> removal_handler) {
    typedef typename gp_t::graph_t Graph;
    typedef typename Graph::EdgeId EdgeId;
    TipsProjector<gp_t> tip_projector(gp);
    return [=](EdgeId e) {
        if (removal_handler) removal_handler(e);
        tip_projector.ProjectTip(e);
    };
}

template<class Graph>
class LowCoverageEdgeRemovingAlgorithm : public PersistentProcessingAlgorithm<Graph,
                                                                              typename Graph::EdgeId,
                                                                              omnigraph::CoverageComparator<Graph>> {
    typedef typename Graph::EdgeId EdgeId;
    typedef PersistentProcessingAlgorithm<Graph, EdgeId, omnigraph::CoverageComparator<Graph>> base;

    const SimplifInfoContainer simplif_info_;
    const std::string condition_str_;
    EdgeRemover<Graph> edge_remover_;

    func::TypedPredicate<EdgeId> remove_condition_;
    func::TypedPredicate<EdgeId> proceed_condition_;

protected:

    void PrepareIteration(double iter_run_progress) override {
        TRACE("Preparing iteration for iterative progress " << iter_run_progress);
        ConditionParser<Graph> parser(this->g(), condition_str_,
                                      simplif_info_, iter_run_progress);
        remove_condition_ = omnigraph::AddAlternativesPresenceCondition(this->g(), parser());
        TRACE("Updated remove condition");
        proceed_condition_ = CoverageUpperBound<Graph>(this->g(), parser.max_coverage_bound());
        TRACE("Updated proceed condition up to coverage " << parser.max_coverage_bound());
    }

    bool Proceed(EdgeId e) const override {
        return proceed_condition_(e);
    }

    bool Process(EdgeId e) override {
        TRACE("Checking edge " << this->g().str(e) << " for the removal condition");
        if (remove_condition_(e)) {
            TRACE("Check passed, removing");
            edge_remover_.DeleteEdge(e);
            return true;
        }
        TRACE("Check not passed");
        return false;
    }

public:
    LowCoverageEdgeRemovingAlgorithm(Graph &g,
                                     const std::string &condition_str,
                                     const SimplifInfoContainer &simplif_info,
                                     std::function<void(EdgeId)> removal_handler = nullptr,
                                     bool canonical_only = true,
                                     bool track_changes = true)
            : base(g, nullptr,
                   canonical_only,
                   omnigraph::CoverageComparator<Graph>(g),
                   track_changes),
              simplif_info_(simplif_info),
              condition_str_(condition_str),
              edge_remover_(g, removal_handler),
              remove_condition_(func::AlwaysFalse<EdgeId>()),
              proceed_condition_(func::AlwaysTrue<EdgeId>()) {

        ConditionParser<Graph> parser(g, condition_str, simplif_info);
        this->interest_el_finder_ =
                std::make_shared<omnigraph::ParallelInterestingElementFinder<Graph>>(
                        AddAlternativesPresenceCondition(g, parser()),
                        simplif_info.chunk_cnt());
    }

private:
    DECL_LOGGER("LowCoverageEdgeRemovingAlgorithm");
};

template<class Graph>
AlternativesAnalyzer<Graph> ParseBRConfig(const Graph &g,
                                          const config::debruijn_config::simplification::bulge_remover &config) {
    size_t max_length = LengthThresholdFinder::MaxBulgeLength(
        g.k(), config.max_bulge_length_coefficient,
        config.max_additive_length_coefficient);

    DEBUG("Length bound " << max_length);

    return AlternativesAnalyzer<Graph>(g, config.max_coverage,
                                       max_length,
                                       config.max_relative_coverage,
                                       config.max_delta,
                                       config.max_relative_delta,
                                       config.max_number_edges,
                                       config.dijkstra_vertex_limit);
}

template<class Graph>
AlgoPtr<Graph> SelfConjugateEdgeRemoverInstance(Graph &g, const string &condition_str,
                const SimplifInfoContainer &info,
                EdgeRemovalHandlerF<Graph> removal_handler = 0) {
    if (condition_str.empty())
        return nullptr;
    ConditionParser<Graph> parser(g, condition_str, info);
    auto condition = func::And(SelfConjugateCondition<Graph>(g), parser());

    return std::make_shared<omnigraph::ParallelEdgeRemovingAlgorithm<Graph>>(g,
                                                                  condition,
                                                                  info.chunk_cnt(),
                                                                  removal_handler,
                                                                  /*canonical_only*/true);
}

template<class Graph>
AlgoPtr<Graph> RelativeCoverageComponentRemoverInstance (
        Graph &g,
        const FlankingCoverage<Graph> &flanking_cov,
        const config::debruijn_config::simplification::relative_coverage_comp_remover &rcc_config,
        const SimplifInfoContainer &info,
        typename ComponentRemover<Graph>::HandlerF removal_handler = nullptr) {
    if (!rcc_config.enabled) {
        return nullptr;
        INFO("Removal of relatively low covered connections disabled");
    }

    //     INFO("Removing relatively low covered connections");
    size_t connecting_path_length_bound = LengthThresholdFinder::MaxErroneousConnectionLength(
            g.k(), rcc_config.max_ec_length_coefficient);

    std::string pics_dir = "";

    double max_coverage = math::ge(rcc_config.max_coverage_coeff, 0.)
                          ? info.detected_coverage_bound() * rcc_config.max_coverage_coeff
                          : std::numeric_limits<double>::max();

    return std::make_shared<omnigraph::simplification::relative_coverage::
        RelativeCoverageComponentRemover<Graph>>(g,
                                                 info.chunk_cnt(),
                                                 flanking_cov,
                                                 rcc_config.coverage_gap,
                                                 size_t(double(info.read_length()) * rcc_config.length_coeff),
                                                 size_t(double(info.read_length()) * rcc_config.tip_allowing_length_coeff),
                                                 connecting_path_length_bound,
                                                 max_coverage,
                                                 removal_handler, rcc_config.vertex_count_limit, pics_dir);
}

template<class Graph>
AlgoPtr<Graph> RelativelyLowCoverageDisconnectorInstance(Graph &g,
        const FlankingCoverage<Graph> &flanking_cov,
        const config::debruijn_config::simplification::relative_coverage_edge_disconnector &rced_config,
        const SimplifInfoContainer &info) {
    if (!rced_config.enabled) {
        INFO("Disconnection of relatively low covered edges disabled");
        return nullptr;
    }
    using Condition=omnigraph::simplification::relative_coverage::RelativeCovDisconnectionCondition<Graph>;

    func::TypedPredicate<EdgeId> condition = Condition(g, flanking_cov, rced_config.diff_mult, rced_config.edge_sum);

    if (math::gr(rced_config.unconditional_diff_mult, 0.)) {
        condition = func::Or(Condition(g, flanking_cov, rced_config.unconditional_diff_mult, 0), condition);
    }

    return std::make_shared<omnigraph::DisconnectionAlgorithm<Graph>>(g,
            condition,
            info.chunk_cnt(),
            nullptr);
}

template<class Graph>
AlgoPtr<Graph> ComplexBRInstance(
    Graph &g,
    config::debruijn_config::simplification::complex_bulge_remover cbr_config,
    const SimplifInfoContainer &info) {
    if (!cbr_config.enabled)
        return nullptr;
    size_t max_length = (size_t) ((double) g.k() * cbr_config.max_relative_length);
    size_t max_diff = cbr_config.max_length_difference;
    return std::make_shared<omnigraph::complex_br::ComplexBulgeRemover<Graph>>(g, max_length,
                                                                               max_diff, info.chunk_cnt());
}

template<class Graph>
AlgoPtr<Graph> ComplexTipClipperInstance(Graph &g,
                     config::debruijn_config::simplification::complex_tip_clipper ctc_conf,
                     const SimplifInfoContainer &info,
                     typename ComponentRemover<Graph>::HandlerF removal_handler = 0) {
    if (!ctc_conf.enabled) {
        INFO("Complex tip clipping disabled");
        return nullptr;
    }

    ConditionParser<Graph> parser(g, ctc_conf.condition, info);
    parser();

    return std::make_shared<omnigraph::ComplexTipClipper<Graph>>(g, ctc_conf.max_relative_coverage,
                                         ctc_conf.max_edge_len,
                                         parser.max_length_bound(), info.chunk_cnt(),
                                         "", removal_handler);
}

template<class Graph>
AlgoPtr<Graph> IsolatedEdgeRemoverInstance(Graph &g,
                                           config::debruijn_config::simplification::isolated_edge_remover ier,
                                           const SimplifInfoContainer &info,
                                           EdgeRemovalHandlerF<Graph> removal_handler = 0) {
    if (!ier.enabled) {
        return nullptr;
    }
    size_t max_length_any_cov = ier.use_rl_for_max_length_any_cov ?
                                std::max(info.read_length(), ier.max_length_any_cov) : ier.max_length_any_cov;
    size_t max_length = ier.use_rl_for_max_length ?
                                std::max(info.read_length(), ier.max_length) : ier.max_length;


    auto condition = func::And(IsolatedEdgeCondition<Graph>(g),
                              func::Or(LengthUpperBound<Graph>(g, max_length_any_cov),
                                      func::And(LengthUpperBound<Graph>(g, max_length),
                                               CoverageUpperBound<Graph>(g, ier.max_coverage))));

    return std::make_shared<omnigraph::ParallelEdgeRemovingAlgorithm<Graph>>(g,
                                                                  condition,
                                                                  info.chunk_cnt(),
                                                                  removal_handler,
                                                                  /*canonical_only*/true);
}

template<class Graph>
AlgoPtr<Graph> RelativeECRemoverInstance(Graph &g,
                                         const config::debruijn_config::simplification::relative_coverage_ec_remover &rcec_config,
                                         const SimplifInfoContainer &info,
                                         EdgeRemovalHandlerF<Graph> removal_handler) {
    if (!rcec_config.enabled)
        return nullptr;

    return std::make_shared<omnigraph::ParallelEdgeRemovingAlgorithm<Graph>>(g,
            AddRelativeCoverageECCondition(g, rcec_config.rcec_ratio,
                                           AddAlternativesPresenceCondition(g, func::TypedPredicate<typename Graph::EdgeId>
                                                   (LengthUpperBound<Graph>(g, rcec_config.max_ec_length)))),
            info.chunk_cnt(), removal_handler, /*canonical_only*/true);
}

template<class Graph>
AlgoPtr<Graph> ECRemoverInstance(Graph &g,
                                 const config::debruijn_config::simplification::erroneous_connections_remover &ec_config,
                                 const SimplifInfoContainer &info,
                                 EdgeRemovalHandlerF<Graph> removal_handler = nullptr) {
    if (ec_config.condition.empty())
        return nullptr;

    return std::make_shared<LowCoverageEdgeRemovingAlgorithm<Graph>>(
            g, ec_config.condition, info, removal_handler);
}

template<class Graph>
AlgoPtr<Graph> TipClipperInstance(Graph &g,
                                  const EdgeConditionT<Graph> &condition,
                                  const SimplifInfoContainer &info,
                                  EdgeRemovalHandlerF<Graph> removal_handler = nullptr,
                                  bool track_changes = true) {
    return make_shared<omnigraph::ParallelEdgeRemovingAlgorithm<Graph, omnigraph::LengthComparator<Graph>>>(g,
                                                                        AddTipCondition(g, condition),
                                                                        info.chunk_cnt(),
                                                                        removal_handler,
                                                                        /*canonical_only*/true,
                                                                        LengthComparator<Graph>(g),
                                                                        track_changes);
}

template<class Graph>
AlgoPtr<Graph> TipClipperInstance(Graph &g,
                                  const config::debruijn_config::simplification::tip_clipper &tc_config,
                                  const SimplifInfoContainer &info,
                                  EdgeRemovalHandlerF<Graph> removal_handler = nullptr) {
    if (tc_config.condition.empty())
        return nullptr;

    ConditionParser<Graph> parser(g, tc_config.condition, info);
    auto condition = parser();
    auto algo = TipClipperInstance(g, condition, info, removal_handler);
    VERIFY_MSG(parser.requested_iterations() != 0, "To disable tip clipper pass empty string");
    if (parser.requested_iterations() == 1) {
        return algo;
    } else {
        return make_shared<LoopedAlgorithm<Graph>>(g, algo, 1, size_t(parser.requested_iterations()),
                /*force primary for all*/ true);
    }
}

template<class Graph>
AlgoPtr<Graph> DeadEndInstance(Graph &g,
                               const config::debruijn_config::simplification::dead_end_clipper &dead_end_config,
                               const SimplifInfoContainer &info,
                               EdgeRemovalHandlerF<Graph> removal_handler) {
    if (!dead_end_config.enabled || dead_end_config.condition.empty())
        return nullptr;

    ConditionParser<Graph> parser(g, dead_end_config.condition, info);
    auto condition = parser();
    return make_shared<omnigraph::ParallelEdgeRemovingAlgorithm<Graph, omnigraph::LengthComparator<Graph>>>(g,
            AddDeadEndCondition(g, condition), info.chunk_cnt(), removal_handler, /*canonical_only*/true,
            LengthComparator<Graph>(g), /*track changes*/true);
}

template<class Graph>
AlgoPtr<Graph> TopologyTipClipperInstance(
    Graph &g,
    const config::debruijn_config::simplification::topology_tip_clipper &ttc_config,
    const SimplifInfoContainer &info,
    EdgeRemovalHandlerF<Graph> removal_handler = nullptr) {

    auto condition
            = func::And(LengthUpperBound<Graph>(g,
                                               LengthThresholdFinder::MaxTipLength(info.read_length(), g.k(), ttc_config.length_coeff)),
                       DefaultUniquenessPlausabilityCondition<Graph>(g,
                                                                     ttc_config.uniqueness_length, ttc_config.plausibility_length));

    return TipClipperInstance(g,
                              condition, info, removal_handler, /*track changes*/false);
}

template<class Graph>
AlgoPtr<Graph> BRInstance(Graph &g,
                          const config::debruijn_config::simplification::bulge_remover &br_config,
                          const SimplifInfoContainer &info,
                          EdgeRemovalHandlerF<Graph> removal_handler = nullptr) {
    if (!br_config.enabled || (br_config.main_iteration_only && !info.main_iteration())) {
        return nullptr;
    }

    auto alternatives_analyzer = ParseBRConfig(g, br_config);

    if (br_config.parallel) {
        INFO("Creating parallel br instance");
        return make_shared<omnigraph::ParallelBulgeRemover<Graph>>(g,
                info.chunk_cnt(),
                br_config.buff_size,
                br_config.buff_cov_diff,
                br_config.buff_cov_rel_diff,
                alternatives_analyzer,
                nullptr,
                removal_handler,
                /*track_changes*/true);
    } else {
        INFO("Creating br instance");
        return make_shared<omnigraph::BulgeRemover<Graph>>(g,
                info.chunk_cnt(),
                alternatives_analyzer,
                nullptr,
                removal_handler,
                /*track_changes*/true);
    }
}

template<class Graph>
AlgoPtr<Graph> LowFlankDisconnectorInstance(Graph &g,
                                           const FlankingCoverage<Graph> &flanking_cov,
                                           double cov_bound,
                                           const SimplifInfoContainer &info,
                                           EdgeRemovalHandlerF<Graph> removal_handler) {
    if (math::ls(cov_bound, 0.)) {
        INFO("Flanking coverage based disconnection disabled");
        return nullptr;
    }

    auto condition = [&,cov_bound] (EdgeId e) {
        return g.OutgoingEdgeCount(g.EdgeStart(e)) > 1
               && math::le(flanking_cov.CoverageOfStart(e), cov_bound);
    };

    return make_shared<omnigraph::DisconnectionAlgorithm<Graph>>(g, condition,
                                                                 info.chunk_cnt(),
                                                                 removal_handler);
}

template<class Graph>
AlgoPtr<Graph> LowCoverageEdgeRemoverInstance(Graph &g,
                                              const config::debruijn_config::simplification::low_covered_edge_remover &lcer_config,
                                              const SimplifInfoContainer &info) {
    if (!lcer_config.enabled) {
        return nullptr;
    }
    VERIFY(info.read_length() > g.k());
    double threshold = lcer_config.coverage_threshold * double(info.read_length() - g.k()) / double(info.read_length());
    INFO("Low coverage edge removal (LCER) activated and will remove edges of coverage lower than " << threshold);
    return make_shared<ParallelEdgeRemovingAlgorithm<Graph, CoverageComparator<Graph>>>
                        (g,
                        CoverageUpperBound<Graph>(g, threshold),
                        info.chunk_cnt(),
                        (EdgeRemovalHandlerF<Graph>)nullptr,
                        /*canonical_only*/true,
                        CoverageComparator<Graph>(g));
}

template<class Graph>
bool RemoveHiddenLoopEC(Graph &g,
                        const FlankingCoverage<Graph> &flanking_cov,
                        double determined_coverage_threshold,
                        double relative_threshold,
                        EdgeRemovalHandlerF<Graph> removal_handler) {
    INFO("Removing loops and rc loops with erroneous connections");
    ECLoopRemover<Graph> hc(g, flanking_cov,
                            determined_coverage_threshold,
                            relative_threshold, removal_handler);
    bool res = hc.Run();
    hc.PrintLoopStats();
    return res;
}

}
}
