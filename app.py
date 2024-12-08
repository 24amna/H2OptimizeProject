import pickle
from datetime import timedelta
from flask import make_response, redirect, url_for
from flask import Flask, render_template, request, redirect, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
import random
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



# Email
EMAIL_ADDRESS = "h2optimizecommunity@gmail.com"
EMAIL_PASSWORD = "786h2optimize2025"

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_COOKIE_NAME'] = 'session'


# Initialize Firebase Admin SDK
cred = credentials.Certificate('h2optimize-3b6cd-firebase-adminsdk-r5hdv-878af1aea2.json')
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
    return render_template('index_t.html')


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
        # Authenticate user
        id_token = request.cookies.get('idToken')
        if not id_token:
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Extract data
        method_name = request.json.get('method_name')
        if not method_name:
            return jsonify({'error': 'Invalid data: Missing method_name'}), 400

        # Reference user's favorites
        favorites_ref = db.reference(f'users/{uid}/favorites')
        favorites = favorites_ref.get() or {}

        # Find the key of the favorite to remove
        favorite_key = next((key for key, value in favorites.items() if value.get('method_name') == method_name), None)

        if favorite_key:
            # Remove the favorite
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
            response = make_response(redirect(url_for('signin')))
            response.set_cookie('name', username, max_age=timedelta(days=1))
            response.set_cookie('email', email, max_age=timedelta(days=1))

            return response

        except Exception as e:
            return str(e)
    return render_template('sign-up.html')


# @app.route('/signin', methods=['GET', 'POST'])
# def signin():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         try:
#             id_token = request.cookies.get('idToken')
#             if not id_token:
#                 return 'No ID token provided', 400
#
#             # Verify the ID token
#             decoded_token = auth.verify_id_token(id_token)
#             uid = decoded_token['uid']
#             print(f"User {uid} signed in successfully.")
#
#             user_ref = db.reference(f'users/{uid}')
#             user_data = user_ref.get()
#
#             if user_data:
#                 session['name'] = user_data.get('name')
#                 session['email'] = user_data.get('email')
#                 print(f"User {uid} signed in successfully. Name: {session['name']}")
#
#             return redirect(url_for('users'))
#         except Exception as e:
#             return str(e)
#     return render_template('sign-in.html')
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

            user_ref = db.reference(f'users/{uid}')
            user_data = user_ref.get()

            if user_data:
                response = make_response(redirect(url_for('users')))
                response.set_cookie('name', user_data.get('name'), max_age=timedelta(days=1))
                response.set_cookie('email', user_data.get('email'), max_age=timedelta(days=1))
                print(f"User {uid} signed in successfully. Name: {user_data.get('name')}")
                print(f"Cookies after setting: {request.cookies}")
                return response
            if user_data:
                category = user_data.get('category')
                if category == 'home':
                    return redirect(url_for('goToIndex'))
                elif category == 'industrial':
                    return redirect(url_for('goToIndus'))
                else:
                    return redirect(url_for('users'))
            
        except Exception as e:
            return str(e)
    return render_template('sign-in.html')


@app.route('/signout')
def signout():
    response = make_response(redirect(url_for('signin')))
    response.delete_cookie('uid')
    print("User signed out, cookie cleared.")
    return response


@app.route('/users')
def users():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return redirect(url_for('signin'))

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Check if the user's category is already set
        user_ref = db.reference(f'users/{uid}')
        user_data = user_ref.get()

        if user_data:
            category = user_data.get('category')
            if category == 'home':
                return redirect(url_for('goToIndex'))
            elif category == 'industrial':
                return redirect(url_for('goToIndus'))

        return render_template('users.html')

    except Exception as e:
        print(f"Error in /users route: {str(e)}")
        return "An error occurred. Please try again.", 500


@app.route('/category')
def category():
    print("route accessed")
    return render_template('category_updated.html')


@app.route('/index')
def index():
    return render_template('index_t.html')


@app.route('/set_category', methods=['POST'])
def set_category():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Parse request data
        data = request.json
        category = data.get('category')

        if not category or category not in ['home', 'industrial']:
            return jsonify({'error': 'Invalid category'}), 400

        # Save category to the database
        user_ref = db.reference(f'users/{uid}')
        user_data = user_ref.get()

        # Allow setting the category only once
        if not user_data.get('category'):
            user_ref.update({'category': category})
            return jsonify({'message': 'Category set successfully'}), 200
        else:
            return jsonify({'error': 'Category already set'}), 409

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_user_category', methods=['GET'])
def get_user_category():
    try:
        id_token = request.cookies.get('idToken')
        if not id_token:
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        user_ref = db.reference(f'users/{uid}')
        user_data = user_ref.get()

        return jsonify({'category': user_data.get('category', None)})

    except Exception as e:
        print(f"Error in get_user_category: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/get_name', methods=['GET'])
def get_name():
    try:
        # Retrieve ID token from cookies
        id_token = request.cookies.get('idToken')
        if not id_token:
            print("ID token is missing.")
            return jsonify({'error': 'User not authenticated'}), 401

        # Decode the token to get user ID
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token.get('uid')
        if not uid:
            print("Invalid token or UID is missing.")
            return jsonify({'error': 'Invalid token or UID missing.'}), 400

        print(f"UID retrieved: {uid}")

        # Fetch user data from Firebase
        user_ref = db.reference(f'users/{uid}')
        user_data = user_ref.get()

        if not user_data:
            print("User data not found in Firebase.")
            return jsonify({'error': 'User data not found.'}), 404

        # Fetch the username
        username = user_data.get('name')
        if username:
            # Store username in session
            session['username'] = username
            print(f"Username retrieved: {username}")
            return jsonify({'username': username}), 200
        else:
            print("Username not available in user data.")
            return jsonify({'error': 'Username not available.'}), 404

    except Exception as e:
        print(f"Error in get_name route: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500


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

            return render_template('category_updated.html', dt_result=classification_result, submitted=True)

        except Exception as e:
            # Handle any error during classification and show an error message on the page
            return render_template('category_updated.html', error=str(e), submitted=False)

    return render_template('category_updated.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        dt_result = request.form['dt_result']
        predicted_methods = predict_and_display_methods(dt_result)

        images = [
            'static/assets/img/bg/element.png',
            'static/assets/img/bg/hose.png',
            'static/assets/img/bg/water.png'
        ]

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

        recommendations_with_images = zip(recommendations, images)

        session['recommendations'] = recommendations

        return render_template('recommends_fixed.html', recommendations_with_images=recommendations_with_images, dt_result=dt_result, committed=True)

    return render_template('recommends_fixed.html')


@app.route('/save_recommendation', methods=['POST'])
def save_recommendation():
    data = request.get_json()
    index = data.get('index')
    print(f"Received index: {index}")

    # Check and save recommendation
    recommendations = session.get('recommendations', [])
    print(f"Session recommendations: {recommendations}")
    if 0 <= index < len(recommendations):
        session['selected_recommendation'] = recommendations[index]
        print(f"Selected recommendation: {session['selected_recommendation']}")
    else:
        print("Invalid index or recommendations not available.")

    return jsonify({"message": "Recommendation saved to session"}), 200


@app.route('/details')
def details():
    try:
        selected_recommendation = session.get('selected_recommendation')
        username = session.get('username')
        id_token = request.cookies.get('idToken')

        if not id_token:
            # Handle error or redirect to login if the token is missing
            return redirect(url_for('login'))

        if not selected_recommendation:
            return redirect(url_for('home'))

        method_name = selected_recommendation.get('method_name')
        description = selected_recommendation.get('description')

        if not method_name or not description:
            return render_template('details.html', error="Recommendation data is incomplete.")

        return render_template(
            'details.html',
            method_name=method_name,
            description=description,
            username=username,
            id_token = id_token
        )

    except Exception as e:
        print(f"Error in details route: {str(e)}")
        return render_template('error.html', message="An unexpected error occurred."), 500


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
        # Authenticate user
        id_token = request.cookies.get('idToken')
        if not id_token:
            print("No ID Token found in cookies.")
            return jsonify({'error': 'User not authenticated'}), 401

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        print(f"Authenticated user UID: {uid}")  # Log the user UID

        # Extract data from the request
        favorite_data = request.json
        method_name = favorite_data.get('method_name')
        description = favorite_data.get('description')

        if not method_name or not description:
            print(f"Invalid data: {favorite_data}")  # Log the invalid data
            return jsonify({'error': 'Invalid data: Missing method_name or description'}), 400

        # Reference user's favorites in Firebase
        favorites_ref = db.reference(f'users/{uid}/favorites')
        existing_favorites = favorites_ref.get() or {}

        # Check for duplicates
        if any(fav.get('method_name') == method_name for fav in existing_favorites.values()):
            print(f"Favorite already exists for method_name: {method_name}")  # Log duplicate
            return jsonify({'error': 'Favorite already exists'}), 409  # Prevent duplicates

        # Save the favorite to the database
        favorites_ref.push({
            'method_name': method_name,
            'description': description
        })
        print(f"Favorite saved: {method_name}, {description}")  # Log the successful save

        return jsonify({'message': 'Favorite saved successfully'}), 200
    except Exception as e:
        print(f"Error saving favorite: {str(e)}")  # Log the error
        return jsonify({'error': str(e)}), 500


@app.route('/get_user_favorites', methods=['GET'])
def get_user_favorites():
    try:
        # Check authentication
        id_token = request.cookies.get('idToken')
        if not id_token:
            print("No idToken found in cookies.")
            return jsonify({'error': 'User not authenticated'}), 401

        # Decode token
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        print(f"Decoded UID: {uid}")

        # Retrieve favorites
        favorites_ref = db.reference(f'users/{uid}/favorites')
        favorites = favorites_ref.get()
        print(f"Favorites retrieved: {favorites}")

        # Return favorites
        return jsonify(favorites or {}), 200
    except Exception as e:
        print(f"Error in get_user_favorites: {str(e)}")
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


def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        # Save email to Firebase
        subscribers_ref = db.reference('subscribers')
        subscribers_ref.push({"email": email})

        return jsonify({'message': 'Subscription successful!'}), 200
    return jsonify({'error': 'Invalid email provided'}), 400


def send_weekly_emails():
    try:
        # Fetch subscribers from Firebase
        subscribers_ref = db.reference('subscribers')
        subscribers = subscribers_ref.get()

        # Fetch reminder emails from Firebase
        reminders_ref = db.reference('reminder_emails')
        reminder_emails = reminders_ref.get()

        if not subscribers or not reminder_emails:
            print("No subscribers or reminder emails available.")
            return

        for subscriber in subscribers.values():
            email = subscriber.get('email')
            if email:
                # Select a random reminder email
                reminder = random.choice(list(reminder_emails.values()))
                send_email(email, reminder['subject'], reminder['body'])

    except Exception as e:
        print(f"Error in sending weekly emails: {e}")


# emails (Monday at 9 AM)
scheduler.add_job(send_weekly_emails, 'cron', day_of_week='mon', hour=9)


if __name__ == '__main__':
    app.run(debug=True)
