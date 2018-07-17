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