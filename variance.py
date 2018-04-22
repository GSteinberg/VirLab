"""VARIANCE"""
import csv
import numpy as np
from scipy import stats

def sigcheck( data, kmers ):

	# PSEUDO CODE
	variances = [] 
	for kmer in kmers:
		kmervals = []
		for vector in vectors:
			for file in vectors[vector]:
				for sequence in vectors[vector][file]:
					kmervals.append(vectors[vector][file][sequence][kmer])
		variances.append(np.var(kmervals))

	stats.zscore(variances)
	
	#append variances to dictionary
	
	if variance not in range(-1, 1):
	#	delete KEY that the variance is representing




