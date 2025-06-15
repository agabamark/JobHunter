# utils.py
from datetime import datetime, timedelta
import json
import os

USERS_FILE = 'users.json'

def save_user(new_user):
    users = load_users()
    users[new_user['email']] = new_user
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user(email):
    users = load_users()
    return users.get(email)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

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
    
