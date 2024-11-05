import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
import pickle

# Load the dataset
df = pd.read_csv('classification_dataset.csv')

# Handle missing values
imputer = SimpleImputer(strategy='mean')
df[['ph', 'Solids', 'Turbidity']] = imputer.fit_transform(df[['ph', 'Solids', 'Turbidity']])

# Encode the target variable
label_encoder = LabelEncoder()
df['classification'] = label_encoder.fit_transform(df['classification'])

# Define features and target
X = df[['ph', 'Solids', 'Turbidity']]
y = df['classification']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Decision Tree Classifier
dt_classifier = DecisionTreeClassifier(random_state=42)
dt_classifier.fit(X_train, y_train)

# Train a K-Nearest Neighbors (KNN) Classifier
knn_classifier = KNeighborsClassifier(n_neighbors=5)
knn_classifier.fit(X_train, y_train)

# Save the trained models and Label Encoder as a pickle file
with open('classification_model.pkl', 'wb') as file:
    pickle.dump((dt_classifier, knn_classifier, label_encoder), file)

print("Models and label encoder saved successfully.")
