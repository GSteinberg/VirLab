"""FASTA PARSER"""
from Bio import SeqIO
import os

# Takes a FASTA file, outputs it as a list of strings
def parse( rootdir ):

	for dirName, subdirList, fileList in os.walk(rootdir):
		# Enter directory if it corresponds to a valid vector
		if dirName in (".\Aedes", ".\Culex", ".\Direct_trans"):
			for filename in fileList:
				# Split file name to obtain file type
				filetype = filename.rsplit(".", 1)[-1]
				if filetype == "fna":
					filetype = "fasta"
				elif filetype == "gbff":
					filetype = "genbank"
				
				records = list(SeqIO.parse(dirName + "\\" + filename, filetype ))
				print(records)
				seq_dict = {}
				for genome in records:
					seq_dict[genome.id] = str(genome.seq)
				return seq_dict
				
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