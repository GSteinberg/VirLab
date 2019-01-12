from sklearn import svm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# IMPORT DATASET
dataset = pd.read_csv(   "significant_k_mers.csv"    )

# DATA PREPROCESSING
X = dataset.drop('Class', axis=1)
y = dataset['Class']

# SPLIT DATASET INTO TRAIN AND TEST SETS
# Pre split
from sklearn.model_selection import train_test_split  
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30)

"""======================================================="""

# PICK A KERNEL AND DEGREE
kernel_choice = 'linear'
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
print("Testing Confusion Matrix")
print(confusion_matrix(y_test,y_pred))
print("Training Confusion Matrix")
print(confusion_matrix(y_train,y_pred2))
print("Testing Classification Report")
print(classification_report(y_test,y_pred))
print("Training Classification Report")
print(classification_report(y_train,y_pred2))

"""
print("Unknown Classification Report")

comparison_arr = np.ndarray(shape=(10,), buffer=np.array([0,1,0,1,1,1,1,1,1,1,0,0,0,0]), dtype=int)
if np.all(u_pred == comparison_arr):
	print("Correct!\n" + str(u_pred) + "\n" + str(comparison_arr))
else:
	print("Incorrect!\n" + str(u_pred) + "\n" + str(comparison_arr))
"""