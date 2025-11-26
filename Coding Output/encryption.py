"""
encryption module
handles file encryption using aes-256-gcm
uses factory and strategy design patterns
"""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

# strategy pattern , interface for encryption
class EncryptionStrategy:
    """strategy pattern - defines how encryption works."""
    
    def encrypt(self, data, key):
        """encrypt data using key."""
        pass
    
    def decrypt(self, encrypted_data, key):
        """decrypt data using key."""
        pass

class AES256GCMStrategy(EncryptionStrategy):
    """implements aes-256-gcm encryption."""
    
    def __init__(self):
        """initialize encryption."""
        self.backend = default_backend()
    
    def encrypt(self, data, key):
        """encrypt the data."""
        # generating random nonce
        nonce = os.urandom(12)
        # creating encryption object
        aesgcm = AESGCM(key)
        # encrypting data
        ciphertext = aesgcm.encrypt(nonce, data, None)
        # return nonce + encrypted data
        return nonce + ciphertext
    
    def decrypt(self, encrypted_data, key):
        """decrypt the data."""
        # getting nonce from first 12 bytes
        nonce = encrypted_data[:12]
        # getting encrypted data
        ciphertext = encrypted_data[12:]
        # creating decryption object
        aesgcm = AESGCM(key)
        # decrypting and return
        return aesgcm.decrypt(nonce, ciphertext, None)

class EncryptionFactory:
    """factory pattern , creates encryption objects."""
    
    @staticmethod
    def create_algorithm(algorithm_name="AES256GCM"):
        """factory method - creates encryption algorithm."""
        if algorithm_name == "AES256GCM":
            return AES256GCMStrategy()
        else:
            raise ValueError("encryption type not supported")

class EncryptionManager:
    """manages encryption using factory and strategy patterns."""
    
    def __init__(self, algorithm_name="AES256GCM"):
        """initialize encryption manager."""
        # using factory to create algorithm
        self.strategy = EncryptionFactory.create_algorithm(algorithm_name)
        # encryption key
        self._key = None  
    
    def generate_key(self):
        """generating random encryption key."""
        self._key = os.urandom(32)  
        return self._key
    
    def set_key(self, key):
        """setting encryption key."""
        if len(key) != 32:
            raise ValueError("key must be 32 bytes")
        self._key = key
    
    def get_key(self):
        """getting current key."""
        return self._key
    
    def derive_key_from_password(self, password):
        """creating key from password."""
        # salt for security
        salt = b"music_copyright_salt"  
        # using pbkdf2 to derive key
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        # taking first 32 bytes
        self._key = key[:32]  
        return self._key
    
    def encrypt_data(self, data):
        """encrypting data using strategy."""
        if self._key is None:
            raise ValueError("need to set key first")
        return self.strategy.encrypt(data, self._key)
    
    def decrypt_data(self, encrypted_data):
        """decrypting data using strategy."""
        if self._key is None:
            raise ValueError("need to set key first")
        return self.strategy.decrypt(encrypted_data, self._key)

