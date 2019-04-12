"""FASTA PARSER"""
from Bio import SeqIO
import os
from genome import Genome

# Takes a FASTA file, outputs it as a list of strings
def parse_dir( rootdir, dataset1, dataset2 ):
	genomes = []
	
	for dirName, subdirList, fileList in os.walk(rootdir):
		# if dataset1 and dataset2 are in VirLab
		if dirName in (rootdir + dataset1, rootdir + dataset2):
			vector = dirName.rsplit("\\", 1)[-1]
		
			for filename in fileList:
				# Split file name to obtain file type
				disease, filetype = filename.rsplit(".", 1)
				if filetype == "fna":
					filetype = "fasta"
				elif filetype == "gbff":
					filetype = "genbank"
								
				# records = list of genomes. Each one having traits
				records = list(SeqIO.parse(dirName + "\\" + filename, filetype))
				chars = set('NWKMRYSBVHDX')
				for genome in records:
					if not any((c in chars) for c in genome):
						my_gen = Genome(vector, disease, str(genome.seq))
						genomes.append(my_gen)
						
	return genomes
						
def parse_files( rootdir, file1, file2 ):
	genomes = []
	
	for dirName, subdirList, fileList in os.walk(rootdir):
		# if file1 and dataset2 are in VirLab
		for filename in fileList:
			if filename in (file1, file2):
				# Split file name to obtain file type
				vector, filetype = filename.rsplit(".", 1)
				if filetype == "fna":
					filetype = "fasta"
				elif filetype == "gbff":
					filetype = "genbank"
								
				# records = list of genomes. Each one having traits
				records = list(SeqIO.parse(filename, filetype))
				chars = set('NWKMRYSBVHDX')
				for genome in records:
					if not any((c in chars) for c in genome):
						my_gen = Genome(vector, "", str(genome.seq))
						genomes.append(my_gen)
						
	return genomes