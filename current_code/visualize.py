import csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def reduce( filename ):
	# CONVERT CSV TO NP ARRAY
	reader = csv.reader( open(filename, 'r'), delimiter=',')
	next(reader)
	reader_list = list(reader)
	X = np.array(reader_list).astype("float")
	
	labels = []
	for i in X:
		labels.append(i[-1])
	X = np.delete(X, -1, 1)

	# USE PCA TO REDUCE ELEMENTS
	"""icpa = PCA( n_components = 50 )
	icpa.fit( X )
	icpa.transform( X )"""

	# CALL TSNE
	model = TSNE( n_components=2 ).fit_transform( X )
	
	# VISUALIZE WITH MATPLOTLIB
	elemt = 0
	genome = 0
	for label in labels:
		if label == 0.0:
			#if genome < 30:
			plt.scatter( model[elemt][0], model[elemt][1], c='blue' )
			"""elif 30 < genome < 60:
				plt.scatter( model[elemt][0], model[elemt][1], c=(.00, .4, .8) )
			elif 60 < genome < 90:
				plt.scatter( model[elemt][0], model[elemt][1], c=(0, .3, .7) )"""
		elif label == 1.0:
			#if 90 < genome < 120:
			plt.scatter( model[elemt][0], model[elemt][1], c='red' )
			"""elif 120 < genome < 150:
				plt.scatter( model[elemt][0], model[elemt][1], c=(.9, .3, .3) )
			elif 150 < genome < 180:
				plt.scatter( model[elemt][0], model[elemt][1], c=(.9, .1, .1) )"""
		elemt+=1
		genome+=1
	#plt.scatter( [i[0] for i in model], [x[1] for x in model] )
	plt.show()
