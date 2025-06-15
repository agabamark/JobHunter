from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import utils
import json
import os
from dotenv import load_dotenv
from middleware import validate_request
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://jobhunter-pro.vercel.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Setup logging
if not app.debug:
    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('JobHunter startup')

@app.route('/api/signup', methods=['POST'])
@limiter.limit("5 per minute")
@validate_request(['email', 'job_keywords', 'country'])
def signup():
    try:
        data = request.json
        
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
            app.logger.error(f"Database error: {str(db_error)}")
            return jsonify({"error": "Failed to save user data"}), 500
            
        return jsonify({
            "message": "Signup successful",
            "trial_end": utils.get_trial_end(user)
        }), 201
    
    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/status')
@limiter.limit("30 per minute")
def trial_status():
    try:
        email = request.args.get('email')
        if not email or not utils.validate_email(email):
            return jsonify({"error": "Valid email parameter is required"}), 400
            
        user = utils.get_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "trial_active": utils.is_trial_active(user),
            "trial_end": utils.get_trial_end(user)
        }), 200
    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/run')
@limiter.limit("10 per minute")
def run_bot():
    try:
        email = request.args.get('email')
        if not email or not utils.validate_email(email):
            return jsonify({"error": "Valid email parameter is required"}), 400
            
        user = utils.get_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if utils.is_trial_active(user):
            return jsonify({
                "message": "Bot executed successfully",
                "status": "active",
                "trial_end": utils.get_trial_end(user)
            }), 200
        
        return jsonify({
            "error": "Trial expired. Please upgrade to continue.",
            "upgrade_url": f"/api/upgrade?email={email}"
        }), 403
    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/upgrade')
@limiter.limit("10 per minute")
def upgrade():
    try:
        email = request.args.get('email')
        if not email or not utils.validate_email(email):
            return jsonify({"error": "Valid email parameter is required"}), 400
            
        user = utils.get_user(email)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        payment_options = utils.get_payment_options(user['country'])
        return jsonify(payment_options), 200
    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health')
def health_check():
    try:
        utils.test_db_connection()
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Error Handlers
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({
        "error": "Internal server error",
        "message": str(e) if app.debug else "An unexpected error occurred"
    }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405

# Security Headers
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == '__main__':
    app.run(port=5000, debug=True)