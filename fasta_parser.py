"""FASTA PARSER"""
# takes a FASTA file outputs it as a list of strings

from Bio import SeqIO

def fasta_parser( to_parse ):
	records = list(SeqIO.parse( to_parse, "fasta")
	for segment in records:
		segment = str(segment.seq)
   	return records

