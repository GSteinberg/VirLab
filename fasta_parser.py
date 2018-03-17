"""FASTA PARSER"""
# takes a FASTA file outputs it as a list of strings

from Bio import SeqIO

def parse( filename ):
	records = list(SeqIO.parse( filename, "fasta" )
	for segment in records:
		segment = str(segment.seq)
   	return records

