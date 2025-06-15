from http.server import BaseHTTPRequestHandler
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Test MongoDB connection
            client.admin.command('ismaster')
            
            self._send_response(200, {
                "status": "healthy",
                "database": "connected"
            })
        except Exception as e:
            self._send_response(500, {
                "status": "unhealthy",
                "error": str(e)
            })

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))