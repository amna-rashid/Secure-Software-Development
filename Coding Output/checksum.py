"""
checksum module
calculates checksums to verify file integrity
uses sha-256 hash function
"""

import hashlib

class ChecksumManager:
    """handling checksum calculations."""
    
    @staticmethod
    def calculate_checksum(data):
        """calculating sha-256 checksum."""
        sha256_hash = hashlib.sha256(data)
        # return as hex string
        return sha256_hash.hexdigest()  
    
    @staticmethod
    def verify_checksum(data, expected_checksum):
        """checking if data matches expected checksum."""
        calculated_checksum = ChecksumManager.calculate_checksum(data)
        return calculated_checksum == expected_checksum
    
    @staticmethod
    def calculate_file_checksum(file_path):
        """calculating checksum for file."""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            return ChecksumManager.calculate_checksum(file_data)
        except FileNotFoundError:
            # file not found
            return None  
        except IOError:
            # error reading file
            return None  

