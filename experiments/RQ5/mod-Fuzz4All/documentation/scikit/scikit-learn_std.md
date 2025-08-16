# scikit-learn Documentation

## 1. What is scikit-learn?

​**scikit-learn**​ is a powerful Python library for machine learning, built on top of NumPy, SciPy, and Matplotlib. It provides simple and efficient tools for data mining and data analysis, supporting both supervised and unsupervised learning.

### Key Features:
- Simple and efficient data analysis tools
- Open source with commercial use (BSD license)
- Wide range of machine learning algorithms
- Excellent documentation and community support
- Seamless integration with Python scientific ecosystem

## 2. Core API Overview

### 2.1 Main Modules

# scikit-learn Documentation

## 1. What is scikit-learn?

​**scikit-learn**​ is a powerful Python library for machine learning, built on top of NumPy, SciPy, and Matplotlib. It provides simple and efficient tools for data mining and data analysis, supporting both supervised and unsupervised learning.

### Key Features:
- Simple and efficient data analysis tools
- Open source with commercial use (BSD license)
- Wide range of machine learning algorithms
- Excellent documentation and community support
- Seamless integration with Python scientific ecosystem

## 2. Core API Overview

### 2.1 Main Modules
sklearn.
├── datasets # Built-in datasets
├── preprocessing # Data preprocessing
├── feature_selection # Feature selection
├── decomposition # Dimensionality reduction
├── model_selection # Model selection & evaluation
├── metrics # Evaluation metrics
├── linear_model # Linear models
├── svm # Support Vector Machines
├── ensemble # Ensemble methods
├── tree # Decision trees
├── cluster # Clustering
└── neural_network # Neural networks

## 3. Common APIs & Usage Examples

### 3.1 Data Preprocessing

```python
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
```
### 3.2 Train-Test Split
```python
from sklearn.model_selection import train_test_split

#Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```
### 3.3 Supervised Learning (Classification)
```python
from sklearn.ensemble import RandomForestClassifier

# Create and train model
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)
```
### 3.4 Unsupervised Learning (Clustering)
```python
from sklearn.cluster import KMeans

# Perform clustering
kmeans = KMeans(n_clusters=3)
kmeans.fit(X)

# Get cluster labels
labels = kmeans.labels_
```
### 3.5 Model Evaluation
```python
from sklearn.metrics import accuracy_score, classification_report

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

# Generate detailed report
report = classification_report(y_test, y_pred)
```
### 4 API Design Principles
​Consistent Interface:
All estimators implement fit(), predict() methods
Hyperparameters set in constructor
​Input Formats:
Accept NumPy arrays or SciPy sparse matrices
Features as X, target as y convention
​Pipelines:
```python
from sklearn.pipeline import make_pipeline
pipe = make_pipeline(StandardScaler(), RandomForestClassifier())
pipe.fit(X_train, y_train)
```
