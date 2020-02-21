from one_hot_dna import one_hot_dna
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob

# from Bio import SeqIO
# import os
# from genome import Genome
# from genome import Read
# import re

PATH = "../../genomes/"
CATEGORIES = ["Aedes", "Culex"]

for category in CATEGORIES:
    path = os.path.join(PATH, "Test_" + category)
    files = glob.glob(path + '/**/*.fasta', recursive=True)
    for file in files:
        # pase fasta file
    # for dirName, subdirList, fileList in os.walk(path):
    #     print(dirName)
    #     print(subdirList)
    #     print(fileList)

    print(files)
# transformations = transforms.Compose([transforms.ToTensor()])
#

# dataset1 =
# dataset2 = 
# # Takes a FASTA file, outputs it as a list of genome objects
# # with vector, disease and seq
# def parse_dir( dataset1, dataset2 ):
# 	genomes = []

	# for dirName, subdirList, fileList in os.walk(".."):
# 		# if dataset1 and dataset2 are in VirLab
# 		if dirName in ("../genomes" + dataset1, "../genomes" + dataset2):
# 			vector = dirName.rsplit("/")[-1]

# 			for filename in fileList:
# 				# Split file name to obtain file type
# 				disease, filetype = filename.rsplit(".", 1)
# 				if filetype == "fna":
# 					filetype = "fasta"
# 				elif filetype == "gbff":
# 					filetype = "genbank"

# 				# records = list of genomes. Each one having traits
# 				records = list(SeqIO.parse(dirName + "/" + filename, filetype))
# 				chars = set('NWKMRYSBVHDX')
# 				for genome in records:
# 					# handle ambiguous genomic data, throw all ambigous files out
# 					if not any((c in chars) for c in genome):
# 						my_gen = Genome(vector, disease, str(genome.seq))
# 						genomes.append(my_gen)

# 	return genomes

# For parsing intermediate read files
# def parse_files( file1, file2 ):
# 	reads = []

# 	for filename in [file1, file2]:
# 		# Split file name to obtain file type, handle diff file types
# 		vector, filetype = re.split('\W+', filename)[-2:]
# 		if filetype == "fna":
# 			filetype = "fasta"
# 		elif filetype == "gbff":
# 			filetype = "genbank"

# 		# records = list of genomes. Each one having traits
# 		records = list(SeqIO.parse(filename, filetype))
# 		chars = set('NWKMRYSBVHDX')
# 		for read in records:
# 			# handle ambiguous genomic data, throw all ambigous files out
# 			if not any((c in chars) for c in read):
# 				my_read = Read(vector, "", str(read.seq))
# 				reads.append(my_read)

# 	return reads




# fasta = ">KY926849.1 Dengue virus 1 isolate PF08/080108-88, complete genome\nCTAACAGTTTTTTATTAGAGAGCAGATCTCTGATGAACAACCAACGGAAAAAGACGGGTCGACCGTCTTT"
# my_hottie = one_hot_dna(fasta)
# print(my_hottie)
# print(my_hottie.name)
# print(my_hottie.sequence)
# print(my_hottie.integer)
# print(my_hottie.onehot)
