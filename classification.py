import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import SMOTE  # Importing SMOTE
import numpy as np
import pickle

# Load the dataset
df = pd.read_csv('classification_dataset.csv')

# Handle missing values
imputer = SimpleImputer(strategy='mean')
df[['ph', 'Solids', 'Turbidity']] = imputer.fit_transform(df[['ph', 'Solids', 'Turbidity']])

# Feature Scaling
scaler = StandardScaler()
df[['ph', 'Solids', 'Turbidity']] = scaler.fit_transform(df[['ph', 'Solids', 'Turbidity']])

# Encode the target variable
label_encoder = LabelEncoder()
df['classification'] = label_encoder.fit_transform(df['classification'])

# Define features and target
X = df[['ph', 'Solids', 'Turbidity']]
y = df['classification']

# Use SMOTE to oversample the minority classes
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Train a Decision Tree Classifier
param_grid_dt = {
    'max_depth': [5, 10, 20, None],
    'min_samples_split': [2, 10, 20],
    'min_samples_leaf': [1, 5, 10]
}
dt_classifier = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid_dt, cv=5)
dt_classifier.fit(X_train, y_train)
y_pred_dt = dt_classifier.predict(X_test)

# Evaluate the Decision Tree Classifier
dt_accuracy = accuracy_score(y_test, y_pred_dt)
dt_classification_report = classification_report(y_test, y_pred_dt)

# Train a K-Nearest Neighbors (KNN) Classifier
param_grid_knn = {
    'n_neighbors': [3, 5, 7, 9],
    'weights': ['uniform', 'distance'],
    'p': [1, 2]  # 1 for Manhattan distance, 2 for Euclidean distance
}
knn_classifier = GridSearchCV(KNeighborsClassifier(), param_grid_knn, cv=5)
knn_classifier.fit(X_train, y_train)
y_pred_knn = knn_classifier.predict(X_test)

# Evaluate the KNN Classifier
knn_accuracy = accuracy_score(y_test, y_pred_knn)
knn_classification_report = classification_report(y_test, y_pred_knn)

# Print results for both models
print("Decision Tree Accuracy:", dt_accuracy)
print("Decision Tree Report:\n", dt_classification_report)

print("KNN Classifier Accuracy:", knn_accuracy)
print("KNN Classifier Report:\n", knn_classification_report)

# Save the best-performing model and label encoder as a pickle file
best_model = dt_classifier if dt_accuracy > knn_accuracy else knn_classifier
with open('classification_model.pkl', 'wb') as file:
    pickle.dump((best_model, label_encoder, scaler), file)

print("Best model and label encoder saved successfully.")

# Function to classify new input data
def classify_water(ph, solids, turbidity):
    # Load models and label encoder from pickle file
    with open('classification_model.pkl', 'rb') as file:
        model, label_encoder, scaler = pickle.load(file)

    new_input = scaler.transform(np.array([[ph, solids, turbidity]]))

    # Predict with the best classifier
    prediction = model.predict(new_input)
    classification = label_encoder.inverse_transform(prediction)[0]

    return classification

