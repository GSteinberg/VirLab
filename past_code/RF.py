from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import pandas as pd

# IMPORT DATASET
dataset = pd.read_csv(   "significant_k_mers.csv"    )

# DATA PREPROCESSING
X = dataset.drop('Class', axis=1)
y = dataset['Class']

# SPLIT DATASET INTO TRAIN AND TEST SETS
from sklearn.model_selection import train_test_split  
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30) 

clf = RandomForestClassifier(n_estimators=100, max_depth=2,
                             random_state=0)
clf.fit(X_train, y_train)

print(clf.feature_importances_)

print(clf.predict(X_test))