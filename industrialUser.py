import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score

# Load the dataset
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

# Split the data into training and testing sets (if needed)
# Typically, for prediction, you don't need to split again if you've already trained the model

# Initialize and train the Random Forest model
rf_Model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_Model.fit(X, y)  # Train on the entire dataset if not already done in a training step


# Function to predict and display top recommended methods
def predict_and_display_Methods(dt_result):
    # Encode dt_result using the category encoder
    dt_result_encoded = category_Encoder.transform([dt_result])[0]

    # Predict the probabilities for the encoded category
    predicted_probabilities = rf_Model.predict_proba([[dt_result_encoded]])

    # Get the top recommended method predictions
    top_n = 3  # Number of top recommendations desired
    top_indices = predicted_probabilities[0].argsort()[-top_n:][::-1]
    predicted_methods_encoded = [rf_Model.classes_[i] for i in top_indices]

    # Decode the predicted method names using the method_name_encoder
    predicted_methods = Method_name_encoder.inverse_transform(predicted_methods_encoded)
    return predicted_methods

