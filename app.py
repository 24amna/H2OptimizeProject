import pickle
from flask import jsonify, make_response
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, auth, db
import pandas as pd
import joblib
import requests

from classification import classify_water
from homeUser import category_encoder, rf_model, method_name_encoder, predict_and_display_methods, data
from industrialUser import category_Encoder, rf_Model, Method_name_encoder, predict_and_display_Methods, datai

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Firebase Admin SDK
cred = credentials.Certificate('h2optimize-firebase-adminsdk.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://h2optimize-3b6cd-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Load the trained models and label encoder
with open('classification_model.pkl', 'rb') as file:
    dt_classifier, knn_classifier, label_encoder = pickle.load(file)


@app.before_request
def before_request():
    print(f"Current session: {session}")


@app.route('/')
def home():
    return render_template('Sign-in.html')


@app.route('/goToIndus')
def goToIndus():
    return render_template('industrial.html')


@app.route('/goToIndex')
def goToIndex():
    return render_template('index.html')


@app.route('/goToGuide')
def goToGuide():
    return render_template('guide.html')


@app.route('/goToguide')
def goToguide():
    return render_template('HomeGuide.html')


@app.route('/goToAbout')
def goToAbout():
    return render_template('about.html')


@app.route('/goToFav')
def goToFav():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return redirect(url_for('signin'))

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Fetch favorites from Firebase
        favorites_ref = db.reference(f'users/{uid}/favorites')
        favorites = favorites_ref.get()

        favorites_list = []
        if favorites:
            favorites_list = [{'method_name': item['method_name'], 'description': item['description']} for item in
                              favorites.values()]

        return render_template('saved.html', favorites=favorites_list)
    except Exception as e:
        return str(e)


@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        method_name = request.json.get('method_name')

        if not method_name:
            return jsonify({'error': 'Invalid data'}), 400

        # Reference to the user's favorites
        favorites_ref = db.reference(f'users/{uid}/favorites')

        # Retrieve all favorites
        favorites = favorites_ref.get()

        # Find the key of the favorite to remove
        favorite_key = None
        for key, value in favorites.items():
            if value.get('method_name') == method_name:
                favorite_key = key
                break

        if favorite_key:
            # Remove the favorite from the database
            favorites_ref.child(favorite_key).delete()
            return jsonify({'message': 'Favorite removed successfully'}), 200
        else:
            return jsonify({'error': 'Favorite not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        try:
            user = auth.create_user(email=email, password=password)
            user_ref = db.reference(f'users/{user.uid}')
            user_ref.set({
                'name': username,
                'email': email,
                'password': password,
            })
            return redirect(url_for('signin'))
        except Exception as e:
            return str(e)
    return render_template('sign-up.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            id_token = request.cookies.get('idToken')
            if not id_token:
                return 'No ID token provided', 400

            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            print(f"User {uid} signed in successfully.")
            return redirect(url_for('category'))
        except Exception as e:
            return str(e)
    return render_template('sign-in.html')


@app.route('/signout')
def signout():
    response = make_response(redirect(url_for('signin')))
    response.delete_cookie('uid')
    print("User signed out, cookie cleared.")
    return response


@app.route('/category')
def category():
    return render_template('category.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/indus')
def indus():
    return render_template('industrial.html')


@app.route('/profile')
def profile():
    return render_template('Profile.html')


@app.route('/classify', methods=['POST'])
def classify():
    if request.method == 'POST':
        try:
            # Get form input values
            ph = float(request.form['ph'])
            solids = float(request.form['tds'])  
            turbidity = float(request.form['turbidity'])

            classification_result = classify_water(ph, solids, turbidity)

            return render_template('index.html', dt_result=classification_result, submitted=True)

        except Exception as e:
            # Handle any error during classification and show an error message on the page
            return render_template('index.html', error=str(e), submitted=False)

    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        dt_result = request.form['dt_result']
        predicted_methods = predict_and_display_methods(dt_result)

        recommendations = []
        for method in predicted_methods:
            method_details = data[data['Method Name'] == method]
            description = method_details['Description'].values[0]
            advantages = method_details['Advantages'].values[0]
            recommendations.append({
                'method_name': method,
                'description': description,
                'advantages': advantages
            })

        session['recommendations'] = recommendations

        return render_template('index.html', recommendations=recommendations, dt_result=dt_result, committed=True)

    return render_template('index.html')


@app.route('/details/<int:index>')
def details(index):
    recommendations = session.get('recommendations', [])

    if 1 <= index <= len(recommendations):
        selected_recommendation = recommendations[index - 1]
        return jsonify(selected_recommendation)

    return jsonify({'error': 'Invalid recommendation index or recommendations not found'})


@app.route('/classifyIndustrial', methods=['POST'])
def classifyIndustrial():
    if request.method == 'POST':
        ph = float(request.form['ph'])
        solids = float(request.form['tds'])
        turbidity = float(request.form['turbidity'])

        dt_classification, knn_classification = classify_water(ph, solids, turbidity)

        return render_template('industrial.html', dt_result=dt_classification, knn_result=knn_classification,
                               submitted=True)

    return render_template('industrial.html')


@app.route('/industrial', methods=['POST'])
def industrial():
    if request.method == 'POST':
        dt_result = request.form['dt_result']
        predicted_methods = predict_and_display_Methods(dt_result)

        recommendationsIndus = []
        for method in predicted_methods:
            method_details = datai[datai['Method Name'] == method]
            description = method_details['Description'].values[0]
            advantages = method_details['Advantages'].values[0]
            recommendationsIndus.append({
                'method_name': method,
                'description': description,
                'advantages': advantages
            })
        session['recommendationsIndus'] = recommendationsIndus
        return render_template('industrial.html', recommendations=recommendationsIndus, dt_result=dt_result,
                               committed=True)

    return render_template('industrial.html')


@app.route('/Indusdetails/<int:index>')
def detailsIndus(index):
    recommendationsIndus = session.get('recommendationsIndus', [])

    if 1 <= index <= len(recommendationsIndus):
        selected_recommendation = recommendationsIndus[index - 1]
        return jsonify(selected_recommendation)

    return jsonify({'error': 'Invalid recommendation industrial or recommendations not found'})


@app.route('/save_favorite', methods=['POST'])
def save_favorite():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        favorite_data = request.json
        method_name = favorite_data.get('method_name')
        description = favorite_data.get('description')

        if not method_name or not description:
            return jsonify({'error': 'Invalid data'}), 400

        # Save the favorite under the user's ID in the database
        db.reference(f'users/{uid}/favorites').push({
            'method_name': method_name,
            'description': description
        })

        return jsonify({'message': 'Favorite saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user_ref = db.reference(f'users/{uid}')
        user_data = user_ref.get()

        if user_data:
            return jsonify({
                'name': user_data.get('name', ''),
                'email': user_data.get('email', ''),
                'password': user_data.get('password', ''),
            })
        else:
            return jsonify({'error': 'User data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        user_ref = db.reference(f'users/{uid}')
        user_ref.update({
            'name': username,
            'email': email,
        })

        if password:
            auth.update_user(uid, password=password)

        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)