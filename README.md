# JobHunterPro - Job Automation Platform

A professional Flask-based job automation platform with trial management and country-specific payment options.

## 🚀 Features

- **User Registration**: Email, job keywords, and country-based signup
- **3-Day Free Trial**: Automatic trial management with expiration tracking
- **Job Automation**: Simulated bot running for active trial users
- **Smart Payment Options**: Country-specific payment methods (Mobile Money for Africa, Cards elsewhere)
- **Status Checking**: Real-time trial and user status monitoring
- **Clean Error Handling**: Professional error responses and validation

## 📁 Project Structure

```
JobHunterPro/
├── main.py              # Flask application
├── utils.py             # Helper functions
├── users.json           # User database (auto-created)
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 🛠️ Setup

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Access the API**:
   - Local: `http://localhost:5000`
   - The app runs on `0.0.0.0:5000` for easy deployment

### Deploy to Glitch

1. Create a new Glitch project
2. Upload all files to your Glitch project
3. Glitch will automatically install dependencies and run the app

### Deploy to CodeSandbox

1. Create a new Python Flask sandbox
2. Copy all files to the sandbox
3. The app will start automatically

## 📝 API Endpoints

### 1. Home
```
GET /
```
Returns welcome message and available endpoints.

### 2. User Signup
```
POST /signup
Content-Type: application/json

{
  "email": "user@example.com",
  "job_keywords": "python developer, remote work",
  "country": "Uganda"
}
```

**Response**: 201 Created
```json
{
  "message": "Signup successful! 3-day free trial started.",
  "user": {
    "email": "user@example.com",
    "country": "Uganda",
    "trial_expires": "2025-06-18T10:30:00"
  }
}
```

### 3. Run Automation
```
GET /run?email=user@example.com
```

**Success Response**: 200 OK
```json
{
  "message": "Job automation running successfully!",
  "status": "active",
  "keywords": "python developer, remote work",
  "trial_expires": "2025-06-18T10:30:00"
}
```

**Trial Expired Response**: 403 Forbidden
```json
{
  "error": "Trial expired. Please upgrade to continue.",
  "upgrade_url": "/upgrade?email=user@example.com"
}
```

### 4. Upgrade Options
```
GET /upgrade?email=user@example.com
```

**For African Countries** (Uganda, Kenya, Nigeria):
```json
{
  "message": "Upgrade to JobHunterPro Premium",
  "country": "Uganda",
  "payment_options": {
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
    ]
  }
}
```

**For Other Countries**:
```json
{
  "payment_options": {
    "primary": "card",
    "options": [
      {
        "provider": "Stripe",
        "link": "https://jobhunterpro.com/pay/stripe",
        "description": "Secure card payment via Stripe"
      }
    ]
  }
}
```

### 5. Check Status
```
GET /status?email=user@example.com
```

**Response**: 200 OK
```json
{
  "email": "user@example.com",
  "country": "Uganda",
  "signup_date": "2025-06-15T10:30:00",
  "trial_expires": "2025-06-18T10:30:00",
  "trial_active": true,
  "status": "trial",
  "job_keywords": "python developer, remote work"
}
```

## 🌍 Supported Countries

### Mobile Money Countries
- Uganda (MTN/Airtel Mobile Money)
- Kenya (MTN/Airtel Mobile Money)
- Nigeria (MTN/Airtel Mobile Money)
- Ghana, Tanzania, Rwanda

### Card Payment Countries
- All other countries use Stripe/PayPal

## 🔧 Customization

### Adding New Payment Methods
Edit `get_payment_options()` in `utils.py`:

```python
def get_payment_options(country):
    # Add your custom payment logic here
    if country.lower() in ['your_country']:
        return {
            "primary": "custom_payment",
            "options": [...]
        }
```

### Extending Trial Period
Modify the trial period in `add_user()` function:

```python
trial_expires = signup_date + timedelta(days=7)  # 7-day trial
```

## 🛡️ Error Handling

The app includes comprehensive error handling:
- Input validation
- User existence checks
- Trial expiration validation
- JSON file operations
- HTTP status codes

## 📊 Data Storage

User data is stored in `users.json` with the following structure:
- Email (unique identifier)
- Job keywords
- Country (for payment options)
- Signup date
- Trial expiration date
- Subscription status

## 🚀 Production Considerations

For production deployment:
1. Replace JSON file storage with a proper database (PostgreSQL, MongoDB)
2. Add authentication/authorization
3. Implement real payment processing
4. Add logging and monitoring
5. Use environment variables for configuration
6. Add rate limiting
7. Implement proper security headers

## 🔍 Testing

Test the API endpoints:

```bash
# Signup
curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","job_keywords":"python developer","country":"Uganda"}'

# Run automation
curl "http://localhost:5000/run?email=test@example.com"

# Check status
curl "http://localhost:5000/status?email=test@example.com"

# Get upgrade options
curl "http://localhost:5000/upgrade?email=test@example.com"
```

## 📄 License

This project is part of JobHunterPro commercial platform.
