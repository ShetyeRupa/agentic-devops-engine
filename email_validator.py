import re

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_email_list(emails: list) -> list:
    """Validate multiple email addresses."""
    return [email for email in emails if validate_email(email)]
