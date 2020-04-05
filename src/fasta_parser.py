"""FASTA PARSER"""
from Bio import SeqIO
import os
from src.genome import Genome
from src.genome import Read
import re

# Takes a FASTA file, outputs it as a list of genome objects
# with vector, disease and seq
def parse_dir( dataset1, dataset2 ):
	genomes = []

#TODO fix empty list

	for dirName, subdirList, fileList in os.walk(".."):
		# if dataset1 and dataset2 are in VirLab
		'''
		print("dir: ", dirName)
		print("subdirs: ", subdirList)
		print("files: ", fileList)
		'''
		if dirName in ("../genomes/" + dataset1, "../genomes/" + dataset2):
			vector = dirName.rsplit("/")[-1]
			#print("dir: ", dirName)

			for filename in fileList:
				# Split file name to obtain file type
				disease, filetype = filename.rsplit(".", 1)
				if filetype == "fna":
					filetype = "fasta"
				elif filetype == "gbff":
					filetype = "genbank"

				# records = list of genomes. Each one having traits
				records = list(SeqIO.parse(dirName + "/" + filename, filetype))
				chars = set('NWKMRYSBVHDX')
				for genome in records:
					# handle ambiguous genomic data, throw all ambigous files out
					if not any((c in chars) for c in genome):
						my_gen = Genome(vector, disease, str(genome.seq))
						genomes.append(my_gen)

	return genomes


# For parsing intermediate read files
def parse_files( file1, file2 ):
	reads = []

	for filename in [file1, file2]:
		# Split file name to obtain file type, handle diff file types
		vector, filetype = re.split('\W+', filename)[-2:]
		if filetype == "fna":
			filetype = "fasta"
		elif filetype == "gbff":
			filetype = "genbank"

		# records = list of genomes. Each one having traits
		records = list(SeqIO.parse(filename, filetype))
		chars = set('NWKMRYSBVHDX')
		for read in records:
			# handle ambiguous genomic data, throw all ambigous files out
			if not any((c in chars) for c in read):
				my_read = Read(vector, "", str(read.seq))
				reads.append(my_read)

	return reads
