"""K-MER CREATOR"""
import fasta_parser as fp
import csv
import kruskal_wallis as kw
import visualize as viz
from genome import Genome
import random
import time

def toZero( list, kmer ):
	list[kmer] = 0
				
def analyze_range( k_min, k_max, rootdir, dataset1, dataset2 ):
	genomes = fp.parse( rootdir, dataset1, dataset2 )
	
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
	
	with open("testing_sig_k_mers.csv", 'w', newline="") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=retlist, extrasaction='ignore')
		writer.writeheader()
		for g in test_data:
			if g.vector == dataset1[1:]:
				g.kmers["Class"] = 0
			elif g.vector == dataset2[1:]:
				g.kmers["Class"] = 1
			
			writer.writerow(g.kmers)
					
		csv_file.flush()
	
	# viz.reduce("significant_k_mers.csv")

def main():
	#k_min, k_max = int(input("Desired k-mer range: ")).split(',')
	#### CHANGE THIS TO THE DIRECTORY VIRLAB IS IN ####
	##  '/home/hayden/VirLab'
	##  '/Users/gppst/VirLab'
	start = time.time()
	analyze_range(3, 5, '/Users/gppst/VirLab', '\Test_Aedes', '\Test_Culex')
	end = time.time()
	print("Time: %.5f" % (end - start))
	
main()