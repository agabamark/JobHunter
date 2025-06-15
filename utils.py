from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file in development
load_dotenv()

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

client = MongoClient(MONGODB_URI)
db = client.jobhunter
users_collection = db.users

# ... rest of your utils.py code ...