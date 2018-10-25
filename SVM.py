from sklearn import svm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# IMPORT DATASET
dataset = pd.read_csv(   "significant_k_mers.csv"    )

# DATA PREPROCESSING
X = dataset.drop('Class', axis=1)
y = dataset['Class']
u = pd.DataFrame()

for i in range(len(y)):
	if y[i] == 2:
		u = u.append( X[] )
		X = X.drop(i)
		y = y.drop(i)
print(u)
	
# SPLIT DATASET INTO TRAIN AND TEST SETS
from sklearn.model_selection import train_test_split  
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30) 

"""======================================================="""

# PICK A KERNEL AND DEGREE
kernel_choice = 'poly'
	# 'linear'  --> used for simple linear classification
	# 'poly'    --> polynomial kernel, pick degree below
	# 'rbf'     --> Gaussian model, long runtime but very accurate
	# 'sigmoid' --> best used for binary classification

degree_choice = 3
	# only used by 'poly', default is 3
	# ignored by all other kernels

"""======================================================="""

# TRAIN ALGORITHM
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix  
svclassifier = SVC(kernel=kernel_choice, degree=degree_choice)
svclassifier.fit(X_train, y_train)

y_pred = svclassifier.predict(X_test)
y_pred2 = svclassifier.predict(X_train)


# EVALUATE ALGORITHM
print(confusion_matrix(y_test,y_pred))
print(confusion_matrix(y_train,y_pred2))
print(classification_report(y_test,y_pred))
print(classification_report(y_train,y_pred2))



"""======================================================="""


"""
# 3D VISUALIZATION (FOR LATER)
def visualize():
	kmers = 
	x = 
	y = 
	plt.scatter(X[;,0], X[:,1], c=y, cmap=plt.cm.coolwarm)
	plt.xlabel('')
	plt.ylabel('')
"""	