from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta
import json
import os
from urllib.parse import parse_qs, urlparse
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
    def do_GET(self):
        try:
            # Parse query parameters
            query = parse_qs(urlparse(self.path).query)
            email = query.get('email', [None])[0]

            if not email:
                self._send_response(400, {
                    "error": "Email parameter is required"
                })
                return

            # Find user
            user = users_collection.find_one({'email': email})
            if not user:
                self._send_response(404, {
                    "error": "User not found"
                })
                return

            # Check trial status
            signup_date = datetime.fromisoformat(user['signup_date'])
            trial_end = signup_date + timedelta(days=3)
            trial_active = datetime.utcnow() < trial_end

            self._send_response(200, {
                "trial_active": trial_active,
                "trial_end": trial_end.isoformat()
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
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()