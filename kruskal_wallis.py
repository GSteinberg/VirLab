""" KRUSKAL-WALLIS TEST """	

from scipy import stats
from itertools import izip
import csv

# TRANSPOSE CSV FIRST (OR MAYBE IN THIS??)

def test ( csv_name ):
	
	# transpose csv_name
	trans_csv = izip(*csv.reader(open( csv_name , "rb")))
	csv.writer(open( csv_name , "wb")).writerows(trans_csv)

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
		row.append(results_of_row)