"""K-MER CREATOR"""
import fasta_parser as fp
import csv
	
#k = k value for k-mer freq analysis
#filename = list of genomes
#Generates csv files of k-mer frequency
def analyze(k, rootdir, style):
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
				if read in kmer_dict:
					kmer_dict[read] += 1
				else:
					kmer_dict[read] = 1
		#make csv file with each row having key ane value
		fname = "%i_mers_in_%s.csv" % (k, filename)
		with open(fname, 'w') as csv_file:
			writer = csv.writer(csv_file)
			for pkey in sorted(kmer_dict.keys()):
				writer.writerow([pkey, kmer_dict[pkey]])
				csv_file.flush()
				
def main():
	k = int(input("Desired k-value: "))
	analyze(k, '.', "aggregate")
	
main()