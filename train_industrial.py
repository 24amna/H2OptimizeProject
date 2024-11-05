import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load the dataset   category_Encoder, rf_Model, Method_name_encoder, predict_and_display_Methods
file_path = 'Industrial_Water_Treatment_Methods.csv'
datai = pd.read_csv(file_path)

# Encode the 'Water Category' column
category_Encoder = LabelEncoder()
datai['Water Category Encoded'] = category_Encoder.fit_transform(datai['Water Category'])

# Create a separate label encoder for the 'Method Name' column
Method_name_encoder = LabelEncoder()
datai['Method Name Encoded'] = Method_name_encoder.fit_transform(datai['Method Name'])

# Define the feature and target variable
X = datai[['Water Category Encoded']]
y = datai['Method Name Encoded']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest model
rf_Model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_Model.fit(X_train, y_train)

# Save the trained model and encoders to disk
model_File = 'industrial_water_treatment_model.pkl'
category_encoder_File = 'category_Encoder.pkl'
method_name_encoder_File = 'Method_name_encoder.pkl'

joblib.dump(rf_Model, model_File)
joblib.dump(category_Encoder, category_encoder_File)
joblib.dump(Method_name_encoder, method_name_encoder_File)

print(f"Model saved to {model_File}")
print(f"Category encoder saved to {category_encoder_File}")
print(f"Method name encoder saved to {method_name_encoder_File}")
