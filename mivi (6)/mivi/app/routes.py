from flask import render_template, request, jsonify, session
from app import app, mongo
from OSMPythonTools.overpass import Overpass

# Initialize Overpass API
overpass = Overpass()

@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signin', methods=['POST'])
def signin():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if user exists in the database
        user = mongo.db.users.find_one({"email": email})
        if user and user.get('password') == password:
            session['email'] = email
            return jsonify({"status": "success", "redirect": "/dashboard"}), 200
        else:
            return jsonify({"message": "Invalid credentials. Please try again."}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        user_data = request.get_json()

        # Extract latitude and longitude from user input
        latitude = user_data.get('latitude')
        longitude = user_data.get('longitude')

        if not latitude or not longitude:
            return jsonify({"message": "Latitude and Longitude are required."}), 400

      
        mongo.db.users.insert_one(user_data)
        return jsonify({"message": "Registration successful!"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    email = session.get('email')
    if not email:
        return render_template('login.html')

    return render_template('dashboard.html', email=email)

@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    try:
        user_email = request.args.get('email')
        if not user_email:
            return jsonify({"message": "Email parameter is missing"}), 400
        
        # Fetch user data from MongoDB
        user = mongo.db.users.find_one({"email": user_email})
        
        if user:
            user_data = {
                "name": user.get('name'),
                "age": user.get('age'),
                "height": user.get('height'),
                "weight": user.get('weight'),
                "bloodGroup": user.get('bloodGroup'),
                "isDiabetic": user.get('isDiabetic'),
                "bp": user.get('bp'),
                "medicalHistory": user.get('medicalHistory'),
                "nearbyHospitalsAndLabs": user.get('nearbyHospitalsAndLabs')  # Include nearby hospitals and labs
            }
            return jsonify(user_data), 200
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500
