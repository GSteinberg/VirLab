"""K-MER CREATOR"""
import fasta_parser as fp
import csv
import kruskal_wallis as kw
import visualize as viz
from genome import Genome
import random
import time
import cProfile
import subprocess
from pathlib import Path

PERCENT_TRAIN = 0.7
MIN_GEN_LEN = 76
MIN_SIG_KMERS = 2
K_MIN = 4
K_MAX = 4
DATASET1 = "Test_Aedes"
DATASET2 = "Test_Culex"
PATH = "../"

# Helper for replacing blanks in kmer signatures with 0s
def toZero( list, kmer ):
	list[kmer] = 0

def analyze_range( k_min, k_max, dataset1, dataset2 ):
	# returns list of genome objs w/ vector, disease, and seq for each obj
	genomes = fp.parse_dir( dataset1, dataset2 )
	#print(genomes)

	# populates kmers member for each gen obj
	# make unique_kmers for next step: filling blanks w zeros
	unique_kmers = set()
	for g in genomes:
		g.populate_dictionary( k_min, k_max )
		for key in g.kmers.keys():
			unique_kmers.add(key)

	# replace blanks with zeros
	# checks if any k-mers not present in all other genomic kmer dictionaries
	# if not found, adds them with a value of 0 so all genomes have the same
	# kmer features
	# Takes over 1/3 of computation time
	for g in genomes:
		for kmer in unique_kmers:
			if kmer not in g.kmers.keys():
				toZero( g.kmers, kmer )
	print("zeros added")

	# split into test and train sets
	random.shuffle(genomes)
	pivot = int(len(genomes) * PERCENT_TRAIN)
	train_data = genomes[:pivot]
	test_data = genomes[pivot:]

	# For compatability with BBMap
	# make fasta file with species 1 test data

	# dataset1[1:] to account for slash
	with open(Path(PATH, "results/test_genomes_1.fasta"), 'w', newline='') as test_file:
		for gen in test_data:
			if len(gen.sequence) >= MIN_GEN_LEN and gen.vector == dataset1:
				test_file.write(str(gen))
				test_file.write("\n\n")
		test_file.flush()

	# make fasta file with species 2 test data
	with open(Path(PATH, "results/test_genomes_2.fasta"), 'w+', newline='') as test_file:
		for gen in test_data:
			if len(gen.sequence) >= MIN_GEN_LEN and gen.vector == dataset2:
				test_file.write(str(gen))
				test_file.write("\n\n")
		test_file.flush()

	# Read simulator
	# test_genomes_1.fasta (genomes) --> test_reads_1.fasta (reads)
	subprocess.check_call(['bash', Path(PATH, "BBMap/randomreads.sh"), \
		Path('ref=' + PATH, 'results/test_genomes_1.fasta'), \
		Path('out=' + PATH, 'results/test_reads_1.fastq'), 'length=110', 'coverage=50', \
		'seed=-1'\
	])


	# test_genomes_2.fasta (genomes) --> test_reads_2.fasta (reads)
	subprocess.check_call(['bash', "../BBMap/randomreads.sh", \
		Path('ref=' + PATH, 'results/test_genomes_2.fasta'), \
		Path('out=' + PATH, 'results/test_reads_2.fastq'), 'length=110', 'coverage=50', \
		'seed=-1'\
	])

	# TRAINING SET
	# make csv file with kmer counts for training set
	filename = Path(PATH, "results/%s-%smers in %s and %s.csv" % \
		(k_min, k_max, dataset1.strip("/")[1], dataset2.strip("/")[1]))
	with open(filename, "w+", newline="") as csv_file:
		fieldnames = []
		for g in train_data:
			for key in sorted(g.kmers.keys()):
				if key not in fieldnames:
					fieldnames.append(key)

		writer = csv.DictWriter(csv_file, fieldnames=sorted(fieldnames))
		writer.writeheader()
		for g in train_data:
			writer.writerow(g.kmers)
		csv_file.flush()

	# flipping it to be compatable with kw_test
	flipped_list = zip(*csv.reader(open(filename, "r")))
	with open(filename, "w+", newline="") as flipped_csv:
		csv_writer = csv.writer(flipped_csv)
		vector_list = ["VECTORS"]
		for g in train_data:
			vector_list.append(g.vector)
		csv_writer.writerow(vector_list)
		csv_writer.writerows(flipped_list)

	# returns list of the most significant k_mers
	# takes about 1/3 of computation time
	sig_kmers = kw.test( filename, dataset1, dataset2 )

	# Make csv for only significant kmers for training
	with open(Path(PATH, "results/training_sig_k_mers.csv", 'w+', newline="")) as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=sig_kmers, extrasaction='ignore')
		writer.writeheader()
		for g in train_data:
			if g.vector == dataset1[1:]:
				g.kmers["Class"] = 0
			elif g.vector == dataset2[1:]:
				g.kmers["Class"] = 1

			writer.writerow(g.kmers)

		csv_file.flush()

	# TESTING
	# making dictionaries for test read collections
	test_reads = fp.parse_files(Path(PATH, 'results/test_reads_1.fastq'), \
		Path(PATH, 'results/test_reads_2.fastq'))

	for r in test_reads:
		r.populate_dictionary( k_min, k_max, sig_kmers )

	for r in test_reads:
		for kmer in sig_kmers:
			if kmer not in r.kmers.keys():
				toZero( r.kmers, kmer )

	with open(Path(PATH, "results/testing_sig_k_mers.csv"), 'w+', newline="") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=sig_kmers, extrasaction='ignore')
		writer.writeheader()

		for r in test_reads:
			if r.num_sig_kmers >= MIN_SIG_KMERS:
				if r.vector == "test_reads_1":
					r.kmers["Class"] = 0
				elif r.vector == "test_reads_2":
					r.kmers["Class"] = 1

				writer.writerow(r.kmers)

		csv_file.flush()

	# viz.reduce("significant_k_mers.csv")

def main():
	analyze_range(K_MIN, K_MAX, DATASET1, DATASET2)

main()