from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import os
from utils import (
    load_users, save_users, add_user, get_user, 
    is_trial_active, get_payment_options
)

app = Flask(__name__)

# Initialize users file if it doesn't exist
if not os.path.exists('users.json'):
    with open('users.json', 'w') as f:
        json.dump({}, f)

@app.route('/')
def home():
    """Welcome endpoint"""
    return jsonify({
        "message": "Welcome to JobHunterPro API",
        "endpoints": {
            "signup": "POST /signup",
            "run": "GET /run?email=",
            "upgrade": "GET /upgrade?email=",
            "status": "GET /status?email="
        }
    })

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup with email, job_keywords, and country"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'job_keywords', 'country']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        email = data['email'].lower().strip()
        job_keywords = data['job_keywords']
        country = data['country']
        
        # Check if user already exists
        users = load_users()
        if email in users:
            return jsonify({
                "error": "User already exists",
                "trial_status": "active" if is_trial_active(users[email]) else "expired"
            }), 409
        
        # Add new user
        user_data = add_user(email, job_keywords, country)
        
        return jsonify({
            "message": "Signup successful! 3-day free trial started.",
            "user": {
                "email": email,
                "country": country,
                "trial_expires": user_data['trial_expires']
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Signup failed: {str(e)}"}), 500

@app.route('/run')
def run_automation():
    """Run job automation if trial is active"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({"error": "Email parameter required"}), 400
        
        email = email.lower().strip()
        user = get_user(email)
        
        if not user:
            return jsonify({"error": "User not found. Please signup first."}), 404
        
        if not is_trial_active(user):
            return jsonify({
                "error": "Trial expired. Please upgrade to continue.",
                "upgrade_url": f"/upgrade?email={email}"
            }), 403
        
        # Simulate running the bot
        print(f"Running bot for {email} with keywords: {user['job_keywords']}")
        
        return jsonify({
            "message": "Job automation running successfully!",
            "status": "active",
            "keywords": user['job_keywords'],
            "trial_expires": user['trial_expires']
        })
        
    except Exception as e:
        return jsonify({"error": f"Automation failed: {str(e)}"}), 500

@app.route('/upgrade')
def upgrade():
    """Show upgrade options based on user's country"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({"error": "Email parameter required"}), 400
        
        email = email.lower().strip()
        user = get_user(email)
        
        if not user:
            return jsonify({"error": "User not found. Please signup first."}), 404
        
        payment_options = get_payment_options(user['country'])
        
        return jsonify({
            "message": "Upgrade to JobHunterPro Premium",
            "country": user['country'],
            "payment_options": payment_options,
            "pricing": {
                "monthly": "$29.99",
                "annual": "$299.99 (Save 17%)"
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Upgrade request failed: {str(e)}"}), 500

@app.route('/status')
def check_status():
    """Check user trial status"""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({"error": "Email parameter required"}), 400
        
        email = email.lower().strip()
        user = get_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        trial_active = is_trial_active(user)
        
        return jsonify({
            "email": email,
            "country": user['country'],
            "signup_date": user['signup_date'],
            "trial_expires": user['trial_expires'],
            "trial_active": trial_active,
            "status": "trial" if trial_active else "expired",
            "job_keywords": user['job_keywords']
        })
        
    except Exception as e:
        return jsonify({"error": f"Status check failed: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # For development
    app.run(debug=True, host='0.0.0.0', port=5000)
