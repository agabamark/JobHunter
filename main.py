# main.py
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import utils
import json

app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        required_fields = ['email', 'job_keywords', 'country']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        user = {
            "email": data['email'],
            "job_keywords": data['job_keywords'],
            "country": data['country'],
            "signup_date": datetime.utcnow().isoformat(),
            "trial_active": True
        }
        
        utils.save_user(user)
        return jsonify({"message": "Signup successful", "trial_end": utils.get_trial_end(user)}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run')
def run_bot():
    email = request.args.get('email')
    user = utils.get_user(email)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if utils.is_trial_active(user):
        print("Running bot")
        return jsonify({"message": "Bot executed successfully"}), 200
    
    return jsonify({"error": "Trial expired. Please upgrade to continue."}), 403

@app.route('/upgrade')
def upgrade():
    email = request.args.get('email')
    user = utils.get_user(email)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    payment_options = utils.get_payment_options(user['country'])
    return jsonify(payment_options), 200

@app.route('/status')
def trial_status():
    email = request.args.get('email')
    user = utils.get_user(email)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "trial_active": utils.is_trial_active(user),
        "trial_end": utils.get_trial_end(user)
    }), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
