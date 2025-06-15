from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import re
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

client = MongoClient(MONGODB_URI)
db = client.jobhunter
users_collection = db.users

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_job_keywords(keywords: List[str]) -> bool:
    return all(isinstance(k, str) and len(k.strip()) > 0 for k in keywords)

def validate_country(country: str) -> bool:
    valid_countries = ['Uganda', 'Kenya', 'Nigeria', 'Ghana', 'Tanzania', 'Rwanda']
    return country in valid_countries or country.strip() != ''

def test_db_connection() -> bool:
    try:
        client.admin.command('ismaster')
        return True
    except Exception as e:
        raise Exception(f"Database connection failed: {str(e)}")

def save_user(user: Dict[str, Any]) -> bool:
    try:
        result = users_collection.update_one(
            {'email': user['email']},
            {'$set': user},
            upsert=True
        )
        return bool(result.acknowledged)
    except Exception as e:
        raise Exception(f"Failed to save user: {str(e)}")

def get_user(email: str) -> Optional[Dict[str, Any]]:
    try:
        return users_collection.find_one({'email': email})
    except Exception as e:
        raise Exception(f"Failed to get user: {str(e)}")

def is_trial_active(user: Dict[str, Any]) -> bool:
    try:
        signup_date = datetime.fromisoformat(user['signup_date'])
        trial_end = signup_date + timedelta(days=3)
        return datetime.utcnow() < trial_end
    except Exception as e:
        raise Exception(f"Failed to check trial status: {str(e)}")

def get_trial_end(user: Dict[str, Any]) -> str:
    try:
        signup_date = datetime.fromisoformat(user['signup_date'])
        return (signup_date + timedelta(days=3)).isoformat()
    except Exception as e:
        raise Exception(f"Failed to get trial end date: {str(e)}")

def get_payment_options(country: str) -> Dict[str, Any]:
    mobile_money_countries = ['Uganda', 'Kenya', 'Nigeria', 'Ghana', 'Tanzania', 'Rwanda']
    
    if country in mobile_money_countries:
        return {
            "method": "Mobile Money",
            "options": [
                {
                    "provider": "MTN Mobile Money",
                    "link": "https://payment.jobhunterpro.com/mtn-momo",
                    "description": "Pay with MTN Mobile Money"
                },
                {
                    "provider": "Airtel Money",
                    "link": "https://payment.jobhunterpro.com/airtel-money",
                    "description": "Pay with Airtel Money"
                }
            ]
        }
    return {
        "method": "Credit Card",
        "options": [
            {
                "provider": "Stripe",
                "link": "https://payment.jobhunterpro.com/stripe",
                "description": "Secure card payment via Stripe"
            }
        ]
    }