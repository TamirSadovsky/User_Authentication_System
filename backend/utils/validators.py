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
    if (
        len(password) < 8 or 
        not re.search(r"[0-9]", password) or 
        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password) or 
        not re.search(r"[a-zA-Z\u0590-\u05FF]", password)  # תו אות עברית או אנגלית
    ):
        return False
    return True

def is_valid_israeli_phone(number: str) -> bool:
    """Validate an Israeli phone number."""
    number = number.strip().replace(" ", "")  # Remove spaces

    # Convert +972 format to local 05X format
    if number.startswith("+972"):
        number = "0" + number[4:]

    pattern = r"^05[012345689]\d{7}$"
    return bool(re.match(pattern, number))