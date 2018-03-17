#K-mer creator
import fasta_parser as fp

#k is k value for k-mer freq analysis
def analyze(k, filename)
	seq_list = fp.parse(filename)
	
    # input is string

    # BODY: iterate window of k-chars and catalog them in dictionary :
    
    # output is dictionary of k-mers with their frequency (ie. k-mer = key, freq = value)
	