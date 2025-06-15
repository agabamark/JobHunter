from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import utils
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        required_fields = ['email', 'job_keywords', 'country']
        
        # Input validation
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
            
        # Data preparation
        user = {
            "email": data['email'],
            "job_keywords": data['job_keywords'],
            "country": data['country'],
            "signup_date": datetime.utcnow().isoformat(),
            "trial_active": True,
            "subscription_status": "trial"
        }
        
        # Try to save user
        try:
            utils.save_user(user)
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")  # For logging
            return jsonify({"error": "Failed to save user data"}), 500
            
        return jsonify({
            "message": "Signup successful",
            "trial_end": utils.get_trial_end(user)
        }), 201
    
    except Exception as e:
        print(f"Server error: {str(e)}")  # For logging
        return jsonify({"error": "Internal server error"}), 500

@app.route('/run')
def run_bot():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter is required"}), 400
            
        user = utils.get_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if utils.is_trial_active(user):
            return jsonify({"message": "Bot executed successfully"}), 200
        
        return jsonify({"error": "Trial expired. Please upgrade to continue."}), 403
    except Exception as e:
        print(f"Server error: {str(e)}")  # For logging
        return jsonify({"error": "Internal server error"}), 500

@app.route('/upgrade')
def upgrade():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter is required"}), 400
            
        user = utils.get_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        payment_options = utils.get_payment_options(user['country'])
        return jsonify(payment_options), 200
    except Exception as e:
        print(f"Server error: {str(e)}")  # For logging
        return jsonify({"error": "Internal server error"}), 500

@app.route('/status')
def trial_status():
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({"error": "Email parameter is required"}), 400
            
        user = utils.get_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "trial_active": utils.is_trial_active(user),
            "trial_end": utils.get_trial_end(user)
        }), 200
    except Exception as e:
        print(f"Server error: {str(e)}")  # For logging
        return jsonify({"error": "Internal server error"}), 500

# Add health check endpoint
@app.route('/health')
def health_check():
    try:
        # Test database connection
        utils.test_db_connection()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# For local development
if __name__ == '__main__':
    app.run(port=5000, debug=True)