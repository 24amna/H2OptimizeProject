import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load the dataset
file_path = 'Home_Water_Treatment_Methods.csv'
data = pd.read_csv(file_path)

# Encode the 'Water Category' column
category_encoder = LabelEncoder()
data['Water Category Encoded'] = category_encoder.fit_transform(data['Water Category'])

# Create a separate label encoder for the 'Method Name' column
method_name_encoder = LabelEncoder()
data['Method Name Encoded'] = method_name_encoder.fit_transform(data['Method Name'])

# Define the feature and target variable
X = data[['Water Category Encoded']]
y = data['Method Name Encoded']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Save the trained model and encoders to disk
model_file = 'home_water_treatment_model.pkl'
category_encoder_file = 'category_encoder.pkl'
method_name_encoder_file = 'method_name_encoder.pkl'

joblib.dump(rf_model, model_file)
joblib.dump(category_encoder, category_encoder_file)
joblib.dump(method_name_encoder, method_name_encoder_file)

print(f"Model saved to {model_file}")
print(f"Category encoder saved to {category_encoder_file}")
print(f"Method name encoder saved to {method_name_encoder_file}")
