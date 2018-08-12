""" KRUSKAL-WALLIS TEST """	

from scipy import stats
import csv

def test ( filename ):
	with open(filename) as csv_file:
		reader = csv.reader( csv_file, delimiter=',' ) 
		line = 0
		vector1_count, vector2_count, vector3_count = 0
		x, y, z = 0
		p_list = []		

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
				p_score = stats.kruskal(x,y,z)[1]
				p_list.append( (row[0], p_score) )
				line+=1

		sorted(p_list, key=lambda x: x[1])
		if (1000 > 0.1*len(p_list)): 
			for i in range(0.1*len(p_list)):
				results = p_list[i]
		else:
			for i in range(1000):
				results = p_list[i]

	return results

