from functools import wraps
from flask import request, jsonify
from typing import List, Callable
import utils

def validate_request(required_fields: List[str]) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                return jsonify({"error": "No data provided"}), 400

            missing_fields = [
                field for field in required_fields 
                if field not in request.json
            ]
            
            if missing_fields:
                return jsonify({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400

            # Validate email if present
            if 'email' in request.json and not utils.validate_email(request.json['email']):
                return jsonify({"error": "Invalid email format"}), 400

            # Validate job keywords if present
            if 'job_keywords' in request.json:
                if not isinstance(request.json['job_keywords'], list):
                    return jsonify({"error": "Job keywords must be a list"}), 400
                if not utils.validate_job_keywords(request.json['job_keywords']):
                    return jsonify({"error": "Invalid job keywords format"}), 400

            # Validate country if present
            if 'country' in request.json and not utils.validate_country(request.json['country']):
                return jsonify({"error": "Invalid country"}), 400

            return f(*args, **kwargs)
        return decorated_function
    return decorator