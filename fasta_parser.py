"""FASTA PARSER"""
from Bio import SeqIO

#Takes a FASTA file, outputs it as a list of strings
def parse( filename ):
	seq_dict = {}
	records = list(SeqIO.parse( filename, "fasta" ))
	for genome in records:
		seq_dict[genome.id] = str(genome.seq)
	return seq_dict