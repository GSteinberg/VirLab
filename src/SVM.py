from sklearn import svm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# IMPORT DATASET
test_dataset = pd.read_csv("../results/training_sig_k_mers.csv")
train_dataset = pd.read_csv("../results/testing_sig_k_mers.csv")

# DATA PREPROCESSING
X_train = train_dataset.drop('Class', axis=1)
y_train = train_dataset['Class']
X_test = test_dataset.drop('Class', axis=1)
y_test = test_dataset['Class']

"""======================================================="""

# PICK A KERNEL AND DEGREE
kernel_choice = 'linear'
	# 'linear'  --> used for simple linear classification
	# 'poly'    --> polynomial kernel, pick degree below - most accurate
	# 'rbf'     --> Gaussian model, long runtime but very accurate
	# 'sigmoid' --> best used for binary classification

degree_choice = 2
	# only used by 'poly', default is 3
	# ignored by all other kernels
	
# gamma_choice = 

"""======================================================="""

# TRAIN ALGORITHM
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix  
svclassifier = SVC(kernel=kernel_choice, degree=degree_choice, cache_size=2000)
svclassifier.fit(X_train, y_train)

y_pred2 = svclassifier.predict(X_train)
y_pred = svclassifier.predict(X_test)

# EVALUATE ALGORITHM
print("Training Confusion Matrix")
print(confusion_matrix(y_train,y_pred2))
print("Testing Confusion Matrix")
print(confusion_matrix(y_test,y_pred))
print("Training Classification Report")
print(classification_report(y_train,y_pred2))
print("Testing Classification Report")
print(classification_report(y_test,y_pred))

#finding wrong predictions	
"""
i = 0
for prediction, label in zip(y_pred, y_test):
	i += 1
	if prediction != label:
		print(i, " has been classified as  ", prediction, " and should be ", label)
		"""