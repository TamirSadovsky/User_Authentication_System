import re # regular expression module for email validation
from email_validator import validate_email, EmailNotValidError 
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        logger.info(f"✅ Email validated successfully: {email}")
        return True
    except EmailNotValidError as e:
        logger.warning(f"❌ Invalid email '{email}': {e}")
        return False

def is_valid_password(password: str) -> bool:
    # Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one digit, and one special character
    if (len(password) < 8 or 
        not re.search(r"[A-Z]", password) or 
        not re.search(r"[a-z]", password) or 
        not re.search(r"[0-9]", password) or 
        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
        return False
    return True