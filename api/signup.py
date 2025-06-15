from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.jobhunter
users_collection = db.users

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Validate required fields
            required_fields = ['email', 'job_keywords', 'country']
            if not all(field in data for field in required_fields):
                self._send_response(400, {
                    "error": "Missing required fields"
                })
                return

            # Create user document
            user = {
                "email": data['email'],
                "job_keywords": data['job_keywords'],
                "country": data['country'],
                "signup_date": datetime.utcnow().isoformat(),
                "trial_active": True,
                "subscription_status": "trial"
            }

            # Save to MongoDB
            users_collection.update_one(
                {'email': user['email']},
                {'$set': user},
                upsert=True
            )

            # Calculate trial end date
            trial_end = (datetime.utcnow() + timedelta(days=3)).isoformat()

            self._send_response(201, {
                "message": "Signup successful",
                "trial_end": trial_end
            })

        except Exception as e:
            print(f"Error: {str(e)}")
            self._send_response(500, {
                "error": "Internal server error"
            })

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()