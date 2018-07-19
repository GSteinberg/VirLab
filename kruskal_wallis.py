""" KRUSKAL-WALLIS TEST """	

from scipy import stats
import csv

def test ( filename ):
	with open(filename) as csv_file:
		reader = csv.reader( csv_file, delimiter=',' ) 
		line = 0
		vector1_count, vector2_count, vector3_count = 0
		x, y, z = 0
		
		for row in reader:
			# if first line get num of kmer counts for each vector
			if line == 0:
				for cell in row:
					if "Aedes" in cell: vector1_count+=1
					elif "Culex" in cell: vector2_count+=1
					elif "Direct_trans" in cell: vector3_count+=1
			else:
				col = 0;
				for cell in row:
					if 1 <= col <= vector1_count: x+=1
					elif vector1_count <= col <= vector2_count: y+=1
					elif col != 0: z+=1
					col+=1
			line+=1
"""
		DONT KNOW WHAT TO DO WITH THIS
		results_of_row = stats.kruskal(x,y,z)[1]
		row.append(results_of_row)
"""