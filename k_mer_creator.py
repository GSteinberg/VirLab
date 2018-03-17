"""K-mer creator"""
import fasta_parser as fp
import csv
	
#k = k value for k-mer freq analysis
#filename = list of genomes
def analyze(k, filename):
	#dictionary: key = genome id, value = DNA sequence
	seq_dict = fp.parse(filename)
	for key in seq_dict.keys():
		kmer_dict = {}
		
		for i in range( len(seq_dict[key])-(k-1) ):
			read = seq_dict[key][i:i+k]
			if read in kmer_dict:
				kmer_dict[read]+=1
			else:
				kmer_dict[read] = 1
		filename = "%i_mers_in_%s.csv" % (k, key)
		with open(filename, 'w') as csv_file:
			writer = csv.writer(csv_file)
			for pkey in sorted(kmer_dict.keys()):
				writer.writerow([pkey, kmer_dict[pkey]])
				csv_file.flush()
				
def main():
	analyze(4, "viral_genomes.fna")
main()