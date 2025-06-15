from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

# Create a client instance
client = MongoClient(MONGODB_URI)
db = client.jobhunter
users_collection = db.users

def test_db_connection():
    """Test database connection"""
    try:
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        return True
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")

def save_user(new_user):
    try:
        result = users_collection.update_one(
            {'email': new_user['email']},
            {'$set': new_user},
            upsert=True
        )
        return bool(result.acknowledged)
    except Exception as e:
        raise Exception(f"Failed to save user: {str(e)}")

def get_user(email):
    try:
        user = users_collection.find_one({'email': email})
        return user
    except Exception as e:
        raise Exception(f"Failed to get user: {str(e)}")

def is_trial_active(user):
    try:
        signup_date = datetime.fromisoformat(user['signup_date'])
        trial_end = signup_date + timedelta(days=3)
        return datetime.utcnow() < trial_end
    except Exception as e:
        raise Exception(f"Failed to check trial status: {str(e)}")

def get_trial_end(user):
    try:
        signup_date = datetime.fromisoformat(user['signup_date'])
        return (signup_date + timedelta(days=3)).isoformat()
    except Exception as e:
        raise Exception(f"Failed to get trial end date: {str(e)}")

def get_payment_options(country):
    mobile_money_countries = ['Uganda', 'Kenya', 'Nigeria']
    
    if country in mobile_money_countries:
        return {
            "method": "Mobile Money",
            "links": [
                "https://payment.jobhunterpro.com/mtn-momo",
                "https://payment.jobhunterpro.com/airtel-momo"
            ]
        }
    return {
        "method": "Credit Card",
        "link": "https://payment.jobhunterpro.com/stripe"
    }