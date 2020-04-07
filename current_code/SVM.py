from sklearn import svm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# IMPORT DATASET
train_dataset = pd.read_csv("../results/training_sig_k_mers.csv")
test_dataset = pd.read_csv("../results/testing_sig_k_mers.csv")

# DATA PREPROCESSING
X_train = train_dataset.drop('Class', axis=1)
y_train = train_dataset['Class']
X_test = test_dataset.drop('Class', axis=1)
y_test = test_dataset['Class']

"""======================================================="""

# PICK A KERNEL AND DEGREE
kernel_choice = 'linear' # originally using poly
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
#from sklearn.svm import NuSVC
from sklearn.metrics import classification_report, confusion_matrix
from sklearn import preprocessing

svclassifier = SVC(kernel=kernel_choice, degree=degree_choice)
svclassifier.fit(X_train, y_train)

y_pred2 = svclassifier.predict(X_train)
y_pred = svclassifier.predict(X_test)

x = svclassifier.decision_function(X_train)
norm = np.linalg.norm(svclassifier.coef_)
dist_x = x/norm

xt = svclassifier.decision_function(X_test)
norm = np.linalg.norm(svclassifier.coef_)
dist_xt = xt/norm

to_del_y = []
for i in range(0, y_pred.size):
	if abs(dist_xt[i]) < 100:
		to_del_y.append(i)

i = len(to_del_y) -1
while(i >= 0):
	y_pred = np.delete(y_pred, to_del_y[i])
	y_test = y_test.drop(y_test.index[i]) # y_test = y_test.drop(y_test.index[i])
	i -= 1
#y_test.drop(y_test.index[to_del_y])
print(type(y_train))
print(type(y_test))
"""
print(y_pred)
print("Final length: ")
print(len(y_pred))
"""
# EVALUATE ALGORITHM
print("Training Confusion Matrix")
print(confusion_matrix(y_train,y_pred2))
print("Testing Confusion Matrix")
print(confusion_matrix(y_test,y_pred))
print("Training Classification Report")
print(classification_report(y_train,y_pred2))
print("Testing Classification Report")
print(classification_report(y_test,y_pred))
"""
# determining side and distance from hyperplane using decision_function
x = svclassifier.decision_function(X_train)
norm = np.linalg.norm(svclassifier.coef_)
dist_x = x/norm

xt = svclassifier.decision_function(X_test)
norm = np.linalg.norm(svclassifier.coef_)
dist_xt = xt/norm
#print(X_test[svclassifier.decision_function(X_train)/np.linalg.norm(svclassifier.coef_) > 5])

#y_train = X_train[abs(x) > 5]
#y_test = X_test[abs(xt) > 5]

y_train = X_train
y_test = X_test

for i in range(0, len(X_train)):
	if dist_x[i] < 5:

for i in range(0, len(X_test)):
	if dist_xt[i] < 5:

clf = svclassifier.fit(y_train, y_test)
y_pred = clf.predict(y_train)
y_pred2 = clf.predict(y_test)

#svclassifier.support_ = np.delete(svclassifier.support_, -1, axis =0)
#svclassifier.support_vectors_ = np.delete(svclassifier.support_vectors_, -1, axis = 0)

print("Training Confusion Matrix pt 2")
print(confusion_matrix(y_train,y_pred2))
print("Testing Confusion Matrix")
print(confusion_matrix(y_test,y_pred))
print("Training Classification Report")
print(classification_report(y_train,y_pred2))
print("Testing Classification Report")
print(classification_report(y_test,y_pred))
"""
"""
clf = NuSVC(nu = 0.1, kernel = kernel_choice)
clf.fit(X_train, y_train)
y_pred2 = clf.predict(X_train)
y_pred = clf.predict(X_test)
"""

#finding wrong predictions
"""
i = 0
for prediction, label in zip(y_pred, y_test):
	i += 1
	if prediction != label:
		print(i, " has been classified as  ", prediction, " and should be ", label)
		"""
