import re

def mask_identifiers(text, mask_char="*", show_last=2):
    """
    Mask sensitive identifiers like phone numbers, account IDs, etc.
    
    Args:
        text (str): Text to mask
        mask_char (str): Character to use for masking
        show_last (int): Number of characters to show at the end
        
    Returns:
        str: Masked text
    """
    if not isinstance(text, str):
        text = str(text)
        
    # If text is short, just mask completely
    if len(text) <= show_last:
        return mask_char * len(text)
    
    # Mask all but the last few characters
    masked_part = mask_char * (len(text) - show_last)
    visible_part = text[-show_last:]
    return masked_part + visible_part


def mask_phone_number(phone):
    """
    Specifically mask phone numbers.
    
    Args:
        phone (str): Phone number to mask
        
    Returns:
        str: Masked phone number
    """
    if not isinstance(phone, str):
        phone = str(phone)
        
    # Remove all non-digit characters for processing
    digits = re.sub(r'\D', '', phone)
    
    # If we have a typical phone number, mask the middle part
    if len(digits) >= 7:
        # Keep country code and last 4 digits
        if digits.startswith('91') and len(digits) > 10:
            country_code = '+91'
            middle_digits = digits[2:-4]
            last_digits = digits[-4:]
            masked_middle = '*' * len(middle_digits)
            return f"{country_code}{masked_middle}{last_digits}"
        elif len(digits) >= 10:
            # Assume it's a standard 10-digit number
            area_code = digits[:3]
            middle_digits = digits[3:-4]
            last_digits = digits[-4:]
            masked_middle = '*' * len(middle_digits)
            return f"{area_code}{masked_middle}{last_digits}"
    
    # For other cases, use general masking
    return mask_identifiers(phone)


def mask_password(password, mask_char="*"):
    """
    Mask passwords for logging.
    
    Args:
        password (str): Password to mask
        mask_char (str): Character to use for masking
        
    Returns:
        str: Masked password
    """
    if not password:
        return ""
    return mask_char * min(len(password), 8)  # Limit to 8 chars for security