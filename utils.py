from pymongo import MongoClient
from datetime import datetime, timedelta
import os

# Get MongoDB connection string from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.jobhunter
users_collection = db.users

def save_user(new_user):
    users_collection.update_one(
        {'email': new_user['email']},
        {'$set': new_user},
        upsert=True
    )

def get_user(email):
    return users_collection.find_one({'email': email})

def load_users():
    return {user['email']: user for user in users_collection.find()}

def is_trial_active(user):
    signup_date = datetime.fromisoformat(user['signup_date'])
    trial_end = signup_date + timedelta(days=3)
    return datetime.utcnow() < trial_end

def get_trial_end(user):
    signup_date = datetime.fromisoformat(user['signup_date'])
    return (signup_date + timedelta(days=3)).isoformat()

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
