""" KRUSKAL-WALLIS TEST """	

from scipy import stats
#from itertools import izip
import csv

# TRANSPOSE CSV FIRST (OR MAYBE IN THIS??)

def test ( filename ):
	
	# transpose filename
	flipped_list = izip(*csv.reader(open( filename , "rb")))
	csv.writer( open(filename, "wb") ).writerows(flipped_list)

	"""
	reader = csv.reader( filename, delimiter=’,’) 
	reader.read(first_row)
	for label in first_row:
		if label == Aedes, aedes-count++
		elif
		else


	for row in reader:
	for count in row:
	if col_number is between 1 and aedescount, add to x
	elif col_num is between aedes_count and culex_count, add to y
	elif col_num != 0, add to z

	results_of_row = stats.kruskal(x,y,z)[1]
	row.append(results_of_row)"""