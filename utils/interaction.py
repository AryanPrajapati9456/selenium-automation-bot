import time
import random
import re

def human_sleep(a=0.2, b=0.6):
    """Sleep for a random amount of time between a and b seconds to mimic human behavior."""
    time.sleep(random.uniform(a, b))


def clean_phone(num):
    """
    Clean and format phone numbers for consistent input.
    
    Args:
        num (str): Phone number string to clean
        
    Returns:
        str: Cleaned and formatted phone number
    """
    num = str(num).strip().replace(" ", "").replace("-", "")

    if num.startswith("+91"):
        return num
    if num.startswith("91"):
        return "+" + num
    if len(num) == 10 and num.isdigit():
        return "+91" + num
    if num.isdigit() and len(num) > 10 and not num.startswith("+"):
        return "+" + num

    if not num.startswith("+"):
        return "+" + num

    return num


def validate_account_data(account):
    """
    Validate account data structure.
    
    Args:
        account (dict): Account data dictionary
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["account_id", "login_identifier", "credential"]
    return all(field in account for field in required_fields)