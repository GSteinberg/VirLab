#k = k value for k-mer freq analysis
#filename = list of genomes
#Generates csv files of k-mer frequency
def analyze_single(k, rootdir, style):
	#seq_dict: dictionary w/ key = genome id, value = DNA sequence
	seq_dict = fp.parse(rootdir)
	
	if style == "sift":
		#iterate through genomes and create individual kmer dictionaries
		for key in seq_dict.keys():
			#iterate through each values of seq_dict: DNA sequences
			#if substring of length k starting at i is not in kmer_dict,
			#add it as key and value 1. Else add and increment value
			kmer_dict = {}
			for i in range( len(seq_dict[key])-(k-1) ):
				read = seq_dict[key][i:i+k]
				if 'N' not in read:
					if read in kmer_dict:
						kmer_dict[read] += 1
					else:
						kmer_dict[read] = 1
				
			#make csv file with each row having key and value
			filename = "%i_mers_in_%s.csv" % (k, key)
			with open(filename, 'w') as csv_file:
				writer = csv.writer(csv_file)
				for pkey in sorted(kmer_dict.keys()):
					writer.writerow([pkey, kmer_dict[pkey]])
					csv_file.flush()
				
	elif style == "aggregate":
	#iterate through genomes to create aggregate dictionary of kmers:
		kmer_dict = {}
		for key in seq_dict.keys():
			for i in range( len(seq_dict[key])-(k-1) ):
				read = seq_dict[key][i:i+k]
				if 'N' not in read:
					if read in kmer_dict:
						kmer_dict[read] += 1
					else:
						kmer_dict[read] = 1
		#make csv file with each row having key and value
		fname = "%i_mers_in_%s.csv" % (k, filename)
		with open(fname, 'w') as csv_file:
			writer = csv.writer(csv_file)
			for pkey in sorted(kmer_dict.keys()):
				writer.writerow([pkey, kmer_dict[pkey]])
				csv_file.flush()
				
# ADD ZEROS	
# checks if any k-mers are not present in all other genomic kmer dictionaries
# if not found, adds them with a value of 0 so all genomes have the same kmer features
for vector in vectors.keys():
	for file in vectors[vector].keys():
		for sequence in vectors[vector][file].keys():
			for kmer in vectors[vector][file][sequence].keys():
			
				[toZero(vectors[i][j][k], kmer) for i in vectors.keys()	for j in vectors[i].keys() \
					for k in vectors[i][j].keys() if kmer not in vectors[i][j][k].keys()]
					
					
	k_mer_creator: 114
	"""for g in test_reads_2:
		g.populate_dictionary( k_min, k_max )
		"""

	k_mer_creator: 119
		"""for g in test_reads_2:
		for kmer in sig_kmers:
			if kmer not in g.kmers.keys():
				toZero( g.kmers, kmer )			
	print("zeros added to test genomes")
	"""

	k_mer_creator: 123
		"""
		for g in test_reads_1:
			g.kmers["Class"] = 0
			writer.writerow(g.kmers)
			
		for g in test_reads_2:
			g.kmers["Class"] = 1
			writer.writerow(g.kmers)
			
		csv_file.flush()
		"""

VISUALIZE CODE

#reduce('significant_k_mers.csv')	
'''
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot

import urllib
import numpy as np


def plot():
	url = "https://raw.githubusercontent.com/GSteinberg/VirLab/master/Vector%20k_mer%20data.csv"
	f = urllib.urlopen(url)
	spectra=np.loadtxt(f, delimiter=',')

	traces = []
	y_raw = spectra[:, 0] # wavelength
	sample_size = spectra.shape[1]-1 
	for i in range(1, sample_size):
		z_raw = spectra[:, i]
		x = []
		y = []
		z = []
		ci = int(255/sample_size*i) # ci = "color index"
		for j in range(0, len(z_raw)):
		    z.append([z_raw[j], z_raw[j]])
		    y.append([y_raw[j], y_raw[j]])
		    x.append([i*2, i*2+1])
		traces.append(dict(
		    z=z,
		    x=x,
		    y=y,
		    colorscale=[ [i, 'rgb(%d,%d,255)'%(ci, ci)] for i in np.arange(0,1.1,0.1) ],
		    showscale=False,
		    type='surface',
		))
	fig = { 'data':traces, 'layout':{'title':'Ribbon Plot'} }
	plotly.offline.plot(fig, filename='ribbon-plot-python')

plot()
'''
