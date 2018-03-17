"""K-mer creator"""
import fasta_parser as fp

#k = k value for k-mer freq analysis
#filename = list of genomes
def analyze(k, filename):
	seq_dict = fp.parse(filename)
	for seq in seq_dict:
		kmer_dict = {}
		for i in xrange( len(seq_dict[seq])-(k-1) ):
			read = my_dict[seq][i:i+k]
			if read in kmer_dict:
				kmer_dict[read]+=1
			else:
				kmer_dict[read] = 1
		filename = "%k_mers_in_%s.csv" % (k, seq)
		with open(filename, 'wb') as csv_file:
			writer = csv.writer(csv_file)
			for key, value in seq_dict.items():
				writer.writerow([key, value])

def main():
	analyze(3, "viral_genomes.fna")