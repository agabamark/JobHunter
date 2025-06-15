from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

client = MongoClient(MONGODB_URI)
db = client.jobhunter
users_collection = db.users

# Helper functions
def is_trial_active(user):
    signup_date = datetime.fromisoformat(user['signup_date'])
    trial_end = signup_date + timedelta(days=3)
    return datetime.utcnow() < trial_end

def get_trial_end(user):
    signup_date = datetime.fromisoformat(user['signup_date'])
    return (signup_date + timedelta(days=3)).isoformat()

def get_payment_options(country):
    mobile_money_countries = ['Uganda', 'Kenya', 'Nigeria']
    return {
        "method": "Mobile Money",
        "links": [
            "https://payment.jobhunterpro.com/mtn-momo",
            "https://payment.jobhunterpro.com/airtel-momo"
        ]
    } if country in mobile_money_countries else {
        "method": "Credit Card",
        "link": "https://payment.jobhunterpro.com/stripe"
    }

# Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ['email', 'job_keywords', 'country']
        if not all(field in data for field in required_fields):
            missing = [f for f in required_fields if f not in data]
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        user = {
            "email": data['email'],
            "job_keywords": data['job_keywords'],
            "country": data['country'],
            "signup_date": datetime.utcnow().isoformat(),
            "trial_active": True,
            "subscription_status": "trial"
        }

        users_collection.update_one(
            {'email': user['email']},
            {'$set': user},
            upsert=True
        )

        return jsonify({
            "message": "Signup successful",
            "trial_end": get_trial_end(user)
        }), 201

    except Exception as e:
        print(f"Error in signup: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/status')
def status():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter required"}), 400

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "trial_active": is_trial_active(user),
            "trial_end": get_trial_end(user)
        }), 200

    except Exception as e:
        print(f"Error in status: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health')
def health():
    try:
        # Test DB connection
        client.admin.command('ismaster')
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# For local development
if __name__ == '__main__':
    app.run(port=5000, debug=True)