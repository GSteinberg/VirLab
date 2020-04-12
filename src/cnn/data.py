from Bio import SeqIO # FASTA reader
import glob
import re
import os

def get_data(fasta_sequences):
    min_len = 9083 # in the dengue_fasta
    sequences = []
    for i, fasta in enumerate(fasta_sequences):
        if i == data_size:
            break
        name, sequence = fasta.id, str(fasta.seq)
        one_hot_sequence = one_hot_encode(sequence.lower())
        if (len(one_hot_sequence) >= min_len):
            one_hot_sequence = one_hot_sequence[0: (min_len-1)]
        sequences.append(np.expand_dims(one_hot_sequence, axis=0))
    # print((np.asarray(sequences, dtype=np.double)).dtype)
    return np.asarray(sequences, dtype=np.double)

# Make dictionary of vector and path
def parse_paths(paths):
    vector_sequences = {}
    filetype = "fasta"

    for file in paths:
        base = os.path.basename(file)
        vector = os.path.splitext(base)[0]

        sequences = list(SeqIO.parse(file, filetype))
        vector_sequences[vector] = sequences

    return vector_sequences

def debug_data(sequences, type):
    title = "Printing information about " + type + " sequences"
    print(title.center(60, "-"))

    counter = 1
    total = 0
    for vector, sequences in sequences.items():
        n = len(sequences)
        subtitle = "\tVector #" + str(counter) + ": " + vector + " has " + str(n) + " sequences"
        print(subtitle)
        counter += 1
        total += n
    print("There are " + str(total) + " " + type + " sequences")
# Get FASTA files from genome directory
aedes_paths = glob.glob("./genomes/aedes/*.fasta")
culex_paths = glob.glob("./genomes/culex/*.fasta")

aedes_sequences = parse_paths(aedes_paths)
culex_sequences = parse_paths(culex_paths)

debug_data(aedes_sequences, "aedes")
debug_data(culex_sequences, "culex")
# aedes_data = get_data(aedes_fasta_sequences)
# aedes_labels = np.ones(data_size)
#
# file = "/Users/alevenberg/research/VirLab/src/cnn/genomes/culex/japanese-encephalitis.fasta"
# filetype = "fasta"
# culex_fasta_sequences = list(SeqIO.parse(file, filetype))
