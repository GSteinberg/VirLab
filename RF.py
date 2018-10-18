from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import pandas as pd

# IMPORT DATASET
dataset = pd.read_csv(   "significant_k_mers.csv"    )

# DATA PREPROCESSING
X = dataset.drop('Class', axis=1)
y = dataset['Class']\

clf = RandomForestClassifier(n_estimators=100, max_depth=2,
                             random_state=0)
clf.fit(X, y)

print(clf.feature_importances_)

print(clf.predict([[0, 0, 0, 0]]))