from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import utils
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

client = MongoClient(MONGODB_URI)
db = client.jobhunter
users_collection = db.users

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        required_fields = ['email', 'job_keywords', 'country']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Create user document
        user = {
            "email": data['email'],
            "job_keywords": data['job_keywords'],
            "country": data['country'],
            "signup_date": datetime.utcnow().isoformat(),
            "trial_active": True,
            "trial_expires": (datetime.utcnow() + timedelta(days=3)).isoformat()
        }
        
        # Save user to MongoDB
        try:
            users_collection.update_one(
                {'email': user['email']},
                {'$set': user},
                upsert=True
            )
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            return jsonify({"error": "Database operation failed"}), 500
        
        return jsonify({
            "message": "Signup successful",
            "trial_end": user['trial_expires']
        }), 201
    
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/run', methods=['GET'])
def run_bot():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter is required"}), 400
            
        user = users_collection.find_one({'email': email})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        trial_end = datetime.fromisoformat(user['trial_expires'])
        if datetime.utcnow() < trial_end:
            return jsonify({"message": "Bot executed successfully"}), 200
        
        return jsonify({"error": "Trial expired. Please upgrade to continue."}), 403
    
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/status', methods=['GET'])
def trial_status():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter is required"}), 400
            
        user = users_collection.find_one({'email': email})
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        trial_end = datetime.fromisoformat(user['trial_expires'])
        is_active = datetime.utcnow() < trial_end
        
        return jsonify({
            "trial_active": is_active,
            "trial_end": user['trial_expires']
        }), 200
    
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# For local development only
if __name__ == '__main__':
    app.run(port=5000, debug=True)