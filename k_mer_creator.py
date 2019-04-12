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

def toZero( list, kmer ):
	list[kmer] = 0
				
def analyze_range( k_min, k_max, rootdir, dataset1, dataset2 ):
	genomes = fp.parse_dir( rootdir, dataset1, dataset2 )
	
	unique_kmers = set()
	for g in genomes:
		g.populate_dictionary( k_min, k_max )
		for key in g.kmers.keys():
			unique_kmers.add(key)

	# replace blanks with zeros
	# checks if any k-mers are not present in all other genomic kmer dictionaries
	# if not found, adds them with a value of 0 so all genomes have the same kmer features
	# this takes over 1/3 of our computation time
	for g in genomes:
		for kmer in unique_kmers:
			if kmer not in g.kmers.keys(): 
				toZero( g.kmers, kmer )
	print("zeros added")
	
	# split into test and train sets
	random.shuffle(genomes)
	pivot = int(len(genomes)*0.7)
	train_data = genomes[:pivot]
	test_data = genomes[pivot:]
	
	# make fasta file with aedes test data
	with open("test_genomes_1.fasta", 'w', newline="") as test_file:
		for gen in test_data:
			if len(gen.sequence) >= 76 and gen.vector == dataset1[1:]:
				test_file.write(str(gen))
				test_file.write("\n\n")
		test_file.flush()
		
	# make fasta file with culex test data
	with open("test_genomes_2.fasta", 'w', newline="") as test_file:
		for gen in test_data:
			if len(gen.sequence) >= 76 and gen.vector == dataset2[1:]:
				test_file.write(str(gen))
				test_file.write("\n\n")
		test_file.flush()
	
	# call BBMap randomread.sh
	# turn testing_genomes.fasta (genomes) into testing_reads.fasta (reads)
	subprocess.call(['bash', "BBMap/randomreads.sh", 'ref=test_genomes_1.fasta', 'out=test_reads_1.fastq', 'length=75', 'coverage=50', 'seed=-1'])
	
	subprocess.call(['bash', "BBMap/randomreads.sh", 'ref=test_genomes_2.fasta', 'out=test_reads_2.fastq', 'length=75', 'coverage=50', 'seed=-1'])
	
	#TRAINING
	#make csv file with each row having key and value
	filename = "%s-%smers in %s and %s.csv" % (k_min, k_max, dataset1.strip("\\"), dataset2.strip("\\"))
	with open(filename, 'w', newline="") as csv_file:
		# Instantiate labels
		fieldnames = []
		# convert to list comprehension
		for g in train_data:
			for key in sorted(g.kmers.keys()):
				if key not in fieldnames:
					fieldnames.append(key)
					
		writer = csv.DictWriter(csv_file, fieldnames=sorted(fieldnames))
		writer.writeheader()
		for g in train_data:
			writer.writerow(g.kmers)
		csv_file.flush()
	
	flipped_list = zip(*csv.reader(open(filename, "r")))
	with open(filename, "w", newline="") as flipped_csv:
		csv_writer = csv.writer(flipped_csv)
		vector_list = []
		vector_list.append("VECTORS")
		for g in genomes:
			vector_list.append(g.vector)
		csv_writer.writerow(vector_list)
		csv_writer.writerows(flipped_list)
		
	# takes about 1/3 of computation time
	retlist = kw.test( filename, dataset1, dataset2 )
		
	# Accepting significant K-mers and making final csv
	with open("training_sig_k_mers.csv", 'w', newline="") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=retlist, extrasaction='ignore')
		writer.writeheader()
		for g in train_data:
			if g.vector == dataset1[1:]:
				g.kmers["Class"] = 0
			elif g.vector == dataset2[1:]:
				g.kmers["Class"] = 1
			
			writer.writerow(g.kmers)
					
		csv_file.flush()
	
	#TESTING
	#making dictionaries for test read collections
	test_reads = fp.parse_files(rootdir, 'test_reads_1.fastq', 'test_reads_2.fastq')
    	
	for g in test_reads:
		g.populate_dictionary( k_min, k_max )
	"""for g in test_reads_2:
		g.populate_dictionary( k_min, k_max )
		"""
	for g in test_reads:
		for kmer in retlist:
			if kmer not in g.kmers.keys():
				toZero( g.kmers, kmer )
	"""for g in test_reads_2:
		for kmer in retlist:
			if kmer not in g.kmers.keys():
				toZero( g.kmers, kmer )			
	print("zeros added to test genomes")
	"""
	
	
	with open("testing_sig_k_mers.csv", 'w', newline="") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=retlist, extrasaction='ignore')
		writer.writeheader()
		"""
		for g in test_reads_1:
			g.kmers["Class"] = 0
			writer.writerow(g.kmers)
			
		for g in test_reads_2:
			g.kmers["Class"] = 1
			writer.writerow(g.kmers)
			
		csv_file.flush()
		"""
		for g in test_reads:
			if g.vector == "test_reads_1":
				g.kmers["Class"] = 0
			elif g.vector == "test_reads_2":
				g.kmers["Class"] = 1
			
			writer.writerow(g.kmers)
					
		csv_file.flush()
	
	# viz.reduce("significant_k_mers.csv")

def main():
	#k_min, k_max = int(input("Desired k-mer range: ")).split(',')
	#### CHANGE THIS TO THE DIRECTORY VIRLAB IS IN ####
	##  '/home/hayden/VirLab'
	##  '/Users/gppst/VirLab'
	analyze_range(4, 5, '/Users/gppst/VirLab', '\Test_Aedes', '\Test_Culex')
	
main()