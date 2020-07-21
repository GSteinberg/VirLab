from sklearn import svm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import time
start_time = time.time()

# IMPORT DATASET
test_dataset = pd.read_csv("../results/testing_sig_k_mers.csv")
train_dataset = pd.read_csv("../results/training_sig_k_mers.csv")

# DATA PREPROCESSING
X_train = train_dataset.drop('Class', axis=1)
y_train = train_dataset['Class']
X_test = test_dataset.drop('Class', axis=1)
y_test = test_dataset['Class']

"""======================================================="""

# TRAIN ALGORITHM
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix  

linear_svclassifier = LinearSVC(dual=False, max_iter=1000)
linear_svclassifier.fit(X_train, y_train)

y_pred2 = linear_svclassifier.predict(X_train)
y_pred = linear_svclassifier.predict(X_test)

# PRINT RUNTIME
print("--- %s seconds ---" % (time.time() - start_time))

# EVALUATE ALGORITHM
print("Training Confusion Matrix")
print(confusion_matrix(y_train,y_pred2))

print("Testing Confusion Matrix")
print(confusion_matrix(y_test,y_pred))

print("Training Classification Report")
print(classification_report(y_train,y_pred2))

print("Testing Classification Report")
print(classification_report(y_test,y_pred))