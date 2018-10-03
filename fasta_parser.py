"""FASTA PARSER"""
from Bio import SeqIO
import os

# Takes a FASTA file, outputs it as a list of strings
def parse( rootdir ):
	vectors = {}
	
	for dirName, subdirList, fileList in os.walk(rootdir):
		# Enter directory if it corresponds to a valid vector
		if dirName in (rootdir + "\#Test_Viruses", rootdir + "\#Test_Host"):
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
	
"""
		# Making array subdirs
		subdirs = []
		print(subdirList)
		if len(subdirList) > 0:
			subdirs = [0] * len(subdirList)
			for i in range( len(subdirList) ):
				subdirs[i] = subdirList[i]
		print(subdirs)
		"""
