""" KRUSKAL-WALLIS TEST """
from scipy import stats
import csv

def test( filename, dataset1, dataset2 ):

	with open(filename) as csv_file:
		reader = csv.reader( csv_file, delimiter=',' ) 
		line = 0
		vector1_count = vector2_count = 0
		x = [0]
		y = [0]
		z = [0]
		
		p_list = [] 
		results = []
		for row in reader:
			# if first line get num of kmer counts for each vector
			if line == 0:
				for cell in row:
					if dataset1[1:] in cell: vector1_count+=1
					elif dataset2[1:] in cell: vector2_count+=1
			else:
				col = 0
				for cell in row:
					if col != 0:
						int_cell = float(cell)
						
						if 1 <= col <= vector1_count: 
							x.append(int_cell)
						elif vector1_count < col <= vector1_count + vector2_count:
							y.append(int_cell)
					
					col+=1
			
				statistic, p_score = stats.kruskal(x,y)
				p_list.append( (row[0], p_score) )
					
			line+=1
		p_list.sort(key=lambda x: x[1])
		
		for i in range( min(1000, int(0.1*len(p_list))) ):
			results.append(p_list[i])
			
		results.append(("Class", 0))
		
		return [i[0] for i in results]