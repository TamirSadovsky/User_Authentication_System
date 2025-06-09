# 🛡️ User Authentication System

A secure and user-friendly authentication system built with Flask, HTML, JavaScript, and CSS.

## 🔐 Core Features

- **User Registration** with strong password and email validation  
- **Password Hashing** using bcrypt  
- **JWT Authentication** for secure session management  
- **Email Verification** with token-based validation  
- **User Dashboard** with protected profile view  
- **Profile Editing** (full name, phone, address)  
- **Logout** with JWT blacklisting  
- **Frontend UI** using HTML, CSS, and modern vanilla JS

---

## 🌟 Bonus Features Implemented

- SQLAlchemy database integration (SQLite)  
- Email verification flow via token link  
- User profile editing capabilities  
- “Remember Me” functionality (30-day JWT)  
- Login rate limiting (3 attempts per minute per user/IP)  
- Proper Git history with commits throughout development  

---

## ⚠️ Known Limitation

Due to time constraints, `verification_token_expiry` is not enforced.  
Email verification still works securely via token validation, but the token does not expire after 1 hour as originally intended.

---

## 📦 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/TamirSadovsky/User_Authentication_System.git
cd User_Authentication_System
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv .venv

# Activate (choose one):
.venv\Scripts\activate        # Windows
source .venv/bin/activate       # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file and add:
```env
SECRET_KEY=Authentication-System
JWT_SECRET_KEY=Authentication-System
EMAIL_ADDRESS=example@gmail.com
EMAIL_PASSWORD=ABCD EFGH HIJK LMNO
SQLALCHEMY_DATABASE_URI=sqlite:///users.db
```

### 5. Initialize Database

The app automatically creates the DB tables:
```python
with app.app_context():
    db.create_all()
```

### 6. Run the App
```bash
python app.py
```

Now visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔌 API Endpoints

### `POST /signup`
Register a new user.
```json
{
  "email": "user@example.com",
  "password": "StrongPass1!"
}
```

---

### `POST /logintoken`
Login and receive a JWT.
```json
{
  "email": "user@example.com",
  "password": "StrongPass1!",
  "remember": true
}
```

- Rate-limited to **3 attempts/minute** per email/IP.
- Requires email to be verified.

---

### `POST /logout`
Logs out the user by blacklisting the token.  
**Requires Authorization header.**

---

### `GET /verify?token=<token>`
Verifies a user’s email using the token received via email.

---

### `GET /profile`
Returns profile information.  
**Requires Authorization header.**

---

### `PUT /profile`
Updates user profile fields.
```json
{
  "full_name": "Max Mustermann",
  "phone_number": "0541234567",
  "address": "Tel Aviv"
}
```
- Validates max length and phone format.

---

## 🧪 Testing Instructions

### Run Tests
```bash
pytest
```

### Covered Scenarios
- Signup: success, duplicate, invalid input  
- Login: success, invalid, unverified  
- Email Verification: valid/invalid/missing tokens  
- Logout: token invalidation  
- Profile: get and update with validations  
- Remember Me: checks long-lived JWT  
- Rate Limiting: enforced after 3 failed attempts  

---

## 📁 Project Structure

```
├── backend/ # Flask backend
│ ├── app.py # Main Flask application
│ ├── config.py # Loads environment variables from .env
│ ├── extensions.py # Flask extensions setup (SQLAlchemy, JWT, Limiter, etc.)
│ ├── models.py # SQLAlchemy user model
│ ├── routes.py # API routes (signup, login, profile, etc.)
│ ├── requirements.txt # Backend dependencies
│ ├── .env # Environment variables (not committed)
│ ├── utils/ # Utility modules
│ │ ├── email_utils.py # Email sending logic
│ │ └── validators.py # Input validation functions
│ ├── templates/
│ │ └── verify_success.html # HTML for email verification success
│ └── tests/ # Pytest test suite
│ ├── conftest.py
│ └── test_features.py
│
├── frontend/ # Frontend HTML, CSS, JS
│ ├── index.html # Main login/signup interface
│ ├── dashboard.html # Authenticated user dashboard
│ ├── verify.html # Verification confirmation page
│ ├── script.js # UI logic
│ ├── styles.css # Modern responsive styles
│ ├── eye.png # Show password icon
│ └── eye-off.png # Hide password icon
│
```

---
