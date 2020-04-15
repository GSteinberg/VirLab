from Bio import SeqIO # FASTA reader
import glob
import re
import os
import numpy as np

def find_min_length(combined_sequences):
    seq_lengths = []
    for value in combined_sequences.values():
        for fasta in value:
            name, sequence = fasta.id, str(fasta.seq)
            seq_lengths.append(len(sequence))
    # Debug
    # print("Minimum length is", min(seq_lengths))
    return min(seq_lengths)

def one_hot_encode(seq):
    # https://en.wikipedia.org/wiki/FASTA_format#Sequence_representation
    ltrdict = {'a':[1,0,0,0],'c':[0,1,0,0],'g':[0,0,1,0],'t':[0,0,0,1], 'b':[0,0,0,0], 'v':[0,0,0,0], 'n':[0,0,0,0], 'd':[0,0,0,0], 'm':[0,0,0,0], 'h':[0,0,0,0], 'w':[0,0,0,0], 'y':[0,0,0,0], 's':[0,0,0,0], 'r':[0,0,0,0], 'k':[0,0,0,0]}
    return [ltrdict[x] for x in seq]

def get_clean_data(fasta_sequences, min_len):
    sequences = []
    # Will take all of them
    for i, fasta in enumerate(fasta_sequences):
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

def combine_sequences(sequences_dictionary):
    return_value = {}
    for vector, value in sequences_dictionary.items():
        vector_sequences = []
        for virus, virus_sequences in value.items():
            vector_sequences.extend(virus_sequences)
        return_value[vector] = vector_sequences
        # Debug
        # print(vector, "vector has", len(vector_sequences), "sequences")
    return return_value

def get_data():
    # Get FASTA files from genome directory
    aedes_paths = glob.glob("./genomes/aedes/*.fasta")
    culex_paths = glob.glob("./genomes/culex/*.fasta")

    aedes_sequences = parse_paths(aedes_paths)
    culex_sequences = parse_paths(culex_paths)
    sequences = {"aedes":aedes_sequences, "culex":culex_sequences}

    aedes = "aedes"
    culex = "culex"

    # debug_data(sequences[aedes],aedes)
    # debug_data(sequences[culex],culex)

    combined_sequences = combine_sequences(sequences)
    min_length = find_min_length(combined_sequences)

    clean_data = {}
    for key, value in combined_sequences.items():
        data = get_clean_data(value, min_length)
        clean_data[key] = data

    return clean_data
