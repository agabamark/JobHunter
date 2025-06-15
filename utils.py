import json
import os
from datetime import datetime, timedelta

def load_users():
    """Load users from JSON file"""
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def add_user(email, job_keywords, country):
    """Add a new user with 3-day trial"""
    users = load_users()
    
    signup_date = datetime.now()
    trial_expires = signup_date + timedelta(days=3)
    
    user_data = {
        'email': email,
        'job_keywords': job_keywords,
        'country': country,
        'signup_date': signup_date.isoformat(),
        'trial_expires': trial_expires.isoformat(),
        'subscription_status': 'trial'
    }
    
    users[email] = user_data
    save_users(users)
    
    return user_data

def get_user(email):
    """Get user data by email"""
    users = load_users()
    return users.get(email)

def is_trial_active(user_data):
    """Check if user's trial is still active"""
    try:
        trial_expires = datetime.fromisoformat(user_data['trial_expires'])
        return datetime.now() < trial_expires
    except (KeyError, ValueError):
        return False

def get_payment_options(country):
    """Get payment options based on country"""
    country = country.lower()
    
    # African countries with mobile money
    mobile_money_countries = ['uganda', 'kenya', 'nigeria', 'ghana', 'tanzania', 'rwanda']
    
    if country in mobile_money_countries:
        return {
            "primary": "mobile_money",
            "options": [
                {
                    "provider": "MTN Mobile Money",
                    "link": "https://jobhunterpro.com/pay/mtn-momo",
                    "description": "Pay with MTN Mobile Money"
                },
                {
                    "provider": "Airtel Money",
                    "link": "https://jobhunterpro.com/pay/airtel-money",
                    "description": "Pay with Airtel Money"
                }
            ],
            "alternative": {
                "provider": "Card Payment",
                "link": "https://jobhunterpro.com/pay/card",
                "description": "Pay with Credit/Debit Card"
            }
        }
    else:
        return {
            "primary": "card",
            "options": [
                {
                    "provider": "Stripe",
                    "link": "https://jobhunterpro.com/pay/stripe",
                    "description": "Secure card payment via Stripe"
                },
                {
                    "provider": "PayPal",
                    "link": "https://jobhunterpro.com/pay/paypal",
                    "description": "Pay with PayPal"
                }
            ]
        }

def cleanup_expired_trials():
    """Helper function to clean up expired trials (optional)"""
    users = load_users()
    active_users = {}
    
    for email, user_data in users.items():
        # Keep all users but could add logic here to archive expired trials
        active_users[email] = user_data
    
    save_users(active_users)
    return len(active_users)

def get_user_stats():
    """Get basic user statistics"""
    users = load_users()
    total_users = len(users)
    active_trials = sum(1 for user in users.values() if is_trial_active(user))
    expired_trials = total_users - active_trials
    
    return {
        "total_users": total_users,
        "active_trials": active_trials,
        "expired_trials": expired_trials
    }
