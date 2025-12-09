"""
PII (Personally Identifiable Information) Protection Utilities
Mask sensitive data in logs and audit trails
"""
import re
from typing import Any, Dict, Optional
import hashlib


class PIIMasker:
    """Utility class for masking PII in data"""
    
    # PII field patterns
    PII_FIELDS = {
        "email", "phone", "address", "ssn", "credit_card", "passport",
        "shipping_address", "shipping_phone", "billing_address",
        "customer_phone", "customer_email", "staff_phone", "staff_email"
    }
    
    # Regex patterns for detecting PII
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b(\+?84|0)[\s.-]?\d{2,3}[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b')
    
    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email address
        Example: john.doe@example.com -> j***@example.com
        """
        if not email or "@" not in email:
            return email
        
        local, domain = email.split("@", 1)
        if len(local) <= 1:
            masked_local = "*"
        else:
            masked_local = local[0] + "***"
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Mask phone number
        Example: 0901234567 -> 090***4567
        """
        if not phone:
            return phone
        
        # Remove non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) < 6:
            return "***"
        
        # Show first 3 and last 4 digits
        return f"{digits[:3]}***{digits[-4:]}"
    
    @staticmethod
    def mask_credit_card(card: str) -> str:
        """
        Mask credit card number
        Example: 1234567890123456 -> ****-****-****-3456
        """
        if not card:
            return card
        
        digits = re.sub(r'\D', '', card)
        
        if len(digits) < 4:
            return "****"
        
        return f"****-****-****-{digits[-4:]}"
    
    @staticmethod
    def mask_address(address: str) -> str:
        """
        Mask address (keep city/province, hide street)
        Example: 123 Main St, District 1, HCMC -> ***, District 1, HCMC
        """
        if not address:
            return address
        
        parts = address.split(",")
        if len(parts) > 1:
            # Mask first part (street address), keep city/province
            masked_parts = ["***"] + parts[1:]
            return ",".join(masked_parts)
        
        return "***"
    
    @staticmethod
    def hash_value(value: str) -> str:
        """
        Create one-way hash of sensitive value
        Useful for tracking unique values without storing actual data
        """
        if not value:
            return ""
        
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    @classmethod
    def mask_dict(cls, data: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
        """
        Recursively mask PII fields in dictionary
        
        Args:
            data: Dictionary to mask
            deep: Whether to recursively mask nested dictionaries
            
        Returns:
            Masked dictionary copy
        """
        if not isinstance(data, dict):
            return data
        
        masked = {}
        
        for key, value in data.items():
            key_lower = key.lower()
            
            # Skip None values
            if value is None:
                masked[key] = value
                continue
            
            # Check if this is a PII field
            is_pii = any(pii_field in key_lower for pii_field in cls.PII_FIELDS)
            
            if is_pii:
                # Apply appropriate masking based on field type
                if isinstance(value, str):
                    if "email" in key_lower:
                        masked[key] = cls.mask_email(value)
                    elif "phone" in key_lower:
                        masked[key] = cls.mask_phone(value)
                    elif "credit" in key_lower or "card" in key_lower:
                        masked[key] = cls.mask_credit_card(value)
                    elif "address" in key_lower:
                        masked[key] = cls.mask_address(value)
                    else:
                        # Generic masking - show first 2 chars
                        masked[key] = value[:2] + "***" if len(value) > 2 else "***"
                else:
                    masked[key] = "***"
            
            elif deep and isinstance(value, dict):
                # Recursively mask nested dictionaries
                masked[key] = cls.mask_dict(value, deep=True)
            
            elif deep and isinstance(value, list):
                # Mask items in lists
                masked[key] = [
                    cls.mask_dict(item, deep=True) if isinstance(item, dict) else item
                    for item in value
                ]
            
            else:
                # Not PII, keep as is
                masked[key] = value
        
        return masked
    
    @classmethod
    def mask_text(cls, text: str) -> str:
        """
        Mask PII patterns found in free text
        
        Args:
            text: Text to scan and mask
            
        Returns:
            Text with PII patterns masked
        """
        if not text:
            return text
        
        # Mask emails
        text = cls.EMAIL_PATTERN.sub(lambda m: cls.mask_email(m.group(0)), text)
        
        # Mask phone numbers
        text = cls.PHONE_PATTERN.sub(lambda m: cls.mask_phone(m.group(0)), text)
        
        # Mask credit cards
        text = cls.CREDIT_CARD_PATTERN.sub(lambda m: cls.mask_credit_card(m.group(0)), text)
        
        return text
    
    @classmethod
    def sanitize_for_audit(cls, data: Any) -> Any:
        """
        Prepare data for audit logging by masking all PII
        
        Args:
            data: Data to sanitize (dict, list, or primitive)
            
        Returns:
            Sanitized copy safe for audit logs
        """
        if isinstance(data, dict):
            return cls.mask_dict(data, deep=True)
        elif isinstance(data, list):
            return [cls.sanitize_for_audit(item) for item in data]
        elif isinstance(data, str):
            return cls.mask_text(data)
        else:
            return data


# Convenience function
def mask_pii(data: Any) -> Any:
    """Shorthand for PIIMasker.sanitize_for_audit()"""
    return PIIMasker.sanitize_for_audit(data)
