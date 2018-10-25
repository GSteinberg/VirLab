"""FASTA PARSER"""
from Bio import SeqIO
import os

# Takes a FASTA file, outputs it as a list of strings
def parse( rootdir, dataset1, dataset2, unknown ):
	vectors = {}
	
	for dirName, subdirList, fileList in os.walk(rootdir):
		# Enter directory if it corresponds to a valid vector
		if dirName in (rootdir + dataset1, rootdir + dataset2, rootdir + unknown):
			diseases = {}
			vectors[dirName.rsplit("\\", 1)[-1]] = diseases
		
			for filename in fileList:
				# Split file name to obtain file type
				filetype = filename.rsplit(".", 1)[-1]
				if filetype == "fna":
					filetype = "fasta"
				elif filetype == "gbff":
					filetype = "genbank"
				
				sequences = {}
				diseases[filename] = sequences
				
				# records = list of genomes. Each one having traits
				records = list(SeqIO.parse(dirName + "\\" + filename, filetype ))
				chars = set('NWKMRYSBVHDX')
				for genome in records:
					if not any((c in chars) for c in genome):
						sequences[genome.id] = str(genome.seq)
				
	return vectors