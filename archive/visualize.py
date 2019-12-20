# IMPORTS
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
