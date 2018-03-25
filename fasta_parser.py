"""FASTA PARSER"""
from Bio import SeqIO

#Takes a FASTA file, outputs it as a list of strings
def parse( filename ):
	seq_dict = {}
	filetype = filename.rsplit(".", 1)[-1]
	print(filetype)
	if filetype == "fna":
		filetype = "fasta"
	elif filetype == "gbff":
		filetype = "genbank"
	records = list(SeqIO.parse( filename, filetype ))
	for genome in records:
		seq_dict[genome.id] = str(genome.seq)
	return seq_dict
