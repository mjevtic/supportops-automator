from cryptography.fernet import Fernet
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key and print it - should be added to .env file
    key = Fernet.generate_key()
    print(f"Generated encryption key: {key.decode()}")
    print("Add this key to your .env file as ENCRYPTION_KEY")
    ENCRYPTION_KEY = key
else:
    # Convert string key back to bytes
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()

cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_value(value):
    """Encrypt a string value"""
    if not value:
        return value
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    """Decrypt an encrypted string value"""
    if not encrypted_value:
        return encrypted_value
    return cipher_suite.decrypt(encrypted_value.encode()).decode()

def encrypt_config(config):
    """
    Encrypt sensitive fields in a config dictionary
    Sensitive fields typically include: api_key, token, password, secret
    """
    if not config:
        return config
    
    # Convert to dict if it's a string
    if isinstance(config, str):
        config = json.loads(config)
    
    sensitive_fields = ['api_key', 'token', 'password', 'secret', 'api_token']
    encrypted_config = config.copy()
    
    for field in sensitive_fields:
        if field in encrypted_config and encrypted_config[field]:
            encrypted_config[field] = encrypt_value(encrypted_config[field])
    
    return encrypted_config

def decrypt_config(encrypted_config):
    """Decrypt sensitive fields in an encrypted config dictionary"""
    if not encrypted_config:
        return encrypted_config
    
    # Convert to dict if it's a string
    if isinstance(encrypted_config, str):
        encrypted_config = json.loads(encrypted_config)
    
    sensitive_fields = ['api_key', 'token', 'password', 'secret', 'api_token']
    decrypted_config = encrypted_config.copy()
    
    for field in sensitive_fields:
        if field in decrypted_config and decrypted_config[field]:
            decrypted_config[field] = decrypt_value(decrypted_config[field])
    
    return decrypted_config
