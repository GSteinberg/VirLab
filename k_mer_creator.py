"""K-MER CREATOR"""
import fasta_parser as fp
#import kruskal_wallis as kw
import csv
#from itertools import izip
	
#k = k value for k-mer freq analysis
#filename = list of genomes
#Generates csv files of k-mer frequency
def analyze_single(k, rootdir, style):
	#seq_dict: dictionary w/ key = genome id, value = DNA sequence
	seq_dict = fp.parse(rootdir)
	
	if style == "sift":
		#iterate through genomes and create individual kmer dictionaries
		for key in seq_dict.keys():
			#iterate through each values of seq_dict: DNA sequences
			#if substring of length k starting at i is not in kmer_dict,
			#add it as key and value 1. Else add and increment value
			kmer_dict = {}
			for i in range( len(seq_dict[key])-(k-1) ):
				read = seq_dict[key][i:i+k]
				if 'N' not in read:
					if read in kmer_dict:
						kmer_dict[read] += 1
					else:
						kmer_dict[read] = 1
				
			#make csv file with each row having key and value
			filename = "%i_mers_in_%s.csv" % (k, key)
			with open(filename, 'w') as csv_file:
				writer = csv.writer(csv_file)
				for pkey in sorted(kmer_dict.keys()):
					writer.writerow([pkey, kmer_dict[pkey]])
					csv_file.flush()
				
	elif style == "aggregate":
	#iterate through genomes to create aggregate dictionary of kmers:
		kmer_dict = {}
		for key in seq_dict.keys():
			for i in range( len(seq_dict[key])-(k-1) ):
				read = seq_dict[key][i:i+k]
				if 'N' not in read:
					if read in kmer_dict:
						kmer_dict[read] += 1
					else:
						kmer_dict[read] = 1
		#make csv file with each row having key and value
		fname = "%i_mers_in_%s.csv" % (k, filename)
		with open(fname, 'w') as csv_file:
			writer = csv.writer(csv_file)
			for pkey in sorted(kmer_dict.keys()):
				writer.writerow([pkey, kmer_dict[pkey]])
				csv_file.flush()

def analyze_range( k_min, k_max, rootdir ):
	#vectors: key = vector_folder, value = diseases
	#	diseases: key = filename, value = sequences
	#		sequences: key = genome id, value = genome sequence
	vectors = fp.parse(rootdir)
	
	#iterate through genomes and create individual kmer dictionaries
	kmer_dict = {}
	
	for vector in vectors.keys():
		for file in vectors[vector].keys():
			for sequence in vectors[vector][file].keys():
					#iterate through each genome in sequences
					#if substring of length k starting at i is not in kmer_dict,
					#add it as key and initialize value as 1. Else add and increment value
					kmers = {}
					for k in range(k_min, k_max+1):
						for i in range( len(vectors[vector][file][sequence])-(k-1) ):
							read = vectors[vector][file][sequence][i:i+k]
							chars = set('NWKMRYSBVHDX')
							if not any((c in chars) for c in read):
								if read in kmers:
									kmers[read] += 1
								else:
									kmers[read] = 1
					vectors[vector][file][sequence] = kmers
					kmer_dict = kmers
	
	# checks if any k-mers are not present in all other genomic kmer dictionaries
	# if not found, adds them with a value of 0 so all genomes have the same kmer features
	for vector in vectors.keys():
		for file in vectors[vector].keys():
			for sequence in vectors[vector][file].keys():
				for kmer in vectors[vector][file][sequence].keys():
					
					for i in vectors.keys():
						for j in vectors[i].keys():
							for k in vectors[i][j].keys():
								if kmer not in vectors[i][j][k].keys():
									vectors[i][j][k][kmer] = 0
	
	#make csv file with each row having key and value
	filename = "Vector k_mer data.csv"
	with open(filename, 'w', newline="") as csv_file:
		# Instantiate labels
		fieldnames = []
		for vector in vectors.keys():
			for file in vectors[vector].keys():
				for sequence in vectors[vector][file].keys():
					for kmer in sorted(vectors[vector][file][sequence].keys()):
						fieldnames.append(kmer)
					if True: break
				if True: break
			if True: break
			
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()
		for vector in vectors.keys():
			for file in vectors[vector].keys():
				for sequence in vectors[vector][file].keys():
					writer.writerow(vectors[vector][file][sequence])
		csv_file.flush()
	
	flipped_list = zip(*csv.reader(open(filename, "r")))
	
	with open(filename, "w", newline="") as flipped_csv:
		csv_writer = csv.writer(flipped_csv)
		vector_list = []
		vector_list.append("VECTORS")
		for vector in vectors.keys():
			for file in vectors[vector].keys():
				for sequence in vectors[vector][file].keys():
					vector_list.append(vector)
		csv_writer.writerow(vector_list)
		csv_writer.writerows(flipped_list)
		
	kw.test(filename)

def main():
	"""k = int(input("Desired k-value: "))
	analyze_single(k, '.', "sift")"""
	
	#k_min, k_max = int(input("Desired k-mer range: ")).split(',')
	analyze_range(4, 5, '/Users/GSteinberg/VirLab')
	
main()
