"""
artefact management module
handles crud operations (create, read, update, delete)
uses observer pattern for timestamps
"""

import os
from datetime import datetime
from database import DatabaseManager
from encryption import EncryptionManager
from checksum import ChecksumManager
from user_manager import User

class ArtefactObserver:
    """observering pattern , listener for changes."""
    
    def on_artefact_modified(self, artefact_id, timestamp):
        """called when artefact is modified."""
        pass

class TimestampObserver(ArtefactObserver):
    """observer that updates timestamps."""
    
    def __init__(self, db_manager):
        """initializing observer."""
        self.db = db_manager
    
    def on_artefact_modified(self, artefact_id, timestamp):
        """update timestamp when artefact modified."""
        # placeholder , timestamp updated in database
        pass

class ArtefactManager:
    """manages all artefact operations."""
    
    def __init__(self, db_manager, encryption_manager):
        """initializing artefact manager."""
        self.db = db_manager
        self.encryption = encryption_manager
        self.checksum_manager = ChecksumManager()
        # list of observers
        self.observers = []  
    
    def add_observer(self, observer):
        """adding observer - observer pattern."""
        self.observers.append(observer)
    
    def _notify_observers(self, artefact_id, timestamp):
        """notify all observers of modification."""
        for observer in self.observers:
            observer.on_artefact_modified(artefact_id, timestamp)
    
    def create_artefact(self, owner, file_path, artefact_name, artefact_type):
        """creating new artefact , create in crud."""
        if artefact_type not in ['lyrics', 'score', 'audio']:
            raise ValueError("Artefact type must be 'lyrics', 'score', or 'audio'")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # reading file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # calculating checksum
            checksum = self.checksum_manager.calculate_checksum(file_data)
            # encrypting file data
            encrypted_data = self.encryption.encrypt_data(file_data)
            
            # showing verification info
            print(f"\n{'='*60}")
            print("FILE UPLOAD VERIFICATION")
            print("="*60)
            print(f"Original file size:   {len(file_data)} bytes")
            print(f"Encrypted data size:  {len(encrypted_data)} bytes")
            print(f"Checksum calculated:  {checksum[:32]}...")
            print(f"File encrypted and checksum stored")
            print("="*60)
            
            # saving to database
            artefact_id = self.db.create_artefact(
                owner_id=owner.user_id,
                artefact_name=artefact_name,
                artefact_type=artefact_type,
                file_path=file_path,
                encrypted_data=encrypted_data,
                checksum=checksum
            )
            
            return artefact_id
            
        except Exception as e:
            print(f"Error creating artefact: {e}")
            return None
    
    def read_artefact(self, artefact_id, user):
        """reading artefact info - read in crud."""
        artefact = self.db.get_artefact(artefact_id)
        if not artefact:
            return None
        
        if not user.can_view_artefact(artefact['owner_id']):
            return None
        
        return {
            'artefact_id': artefact['artefact_id'],
            'artefact_name': artefact['artefact_name'],
            'artefact_type': artefact['artefact_type'],
            'created_at': artefact['created_at'],
            'modified_at': artefact['modified_at'],
            'checksum': artefact['checksum']
        }
    
    def get_artefact_data(self, artefact_id, user, output_path=None):
        """getting and decrypting artefact data."""
        artefact = self.db.get_artefact(artefact_id)
        if not artefact:
            return None
        
        if not user.can_view_artefact(artefact['owner_id']):
            return None
        
        try:
            decrypted_data = self.encryption.decrypt_data(artefact['encrypted_data'])
            calculated_checksum = self.checksum_manager.calculate_checksum(decrypted_data)
            
            # verification output
            print(f"\n{'='*60}")
            print("VERIFICATION: Encryption/Decryption Check")
            print("="*60)
            print(f"Encrypted data size: {len(artefact['encrypted_data'])} bytes")
            print(f"Decrypted data size: {len(decrypted_data)} bytes")
            print(f"Stored checksum:     {artefact['checksum'][:32]}...")
            print(f"Calculated checksum: {calculated_checksum[:32]}...")
            
            if calculated_checksum != artefact['checksum']:
                print("WARNING: Checksum mismatch! Data may have been tampered with.")
                print("="*60)
                return None
            
            print("Checksum verification: PASSED")
            print("Original file = Decrypted file (verified by checksum)")
            print("="*60)
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(decrypted_data)
            
            return decrypted_data
            
        except Exception as e:
            error_msg = str(e) if str(e) else f"{type(e).__name__}"
            print(f"Error retrieving artefact: {error_msg}")
            return None
    
    def update_artefact(self, artefact_id, new_file_path, user):
        """updating artefact , updating in crud."""
        artefact = self.db.get_artefact(artefact_id)
        if not artefact:
            return False
        
        if not user.can_modify_artefact(artefact['owner_id']):
            print("Permission denied: You can only modify your own artefacts.")
            return False
        
        if not os.path.exists(new_file_path):
            raise FileNotFoundError(f"File not found: {new_file_path}")
        
        try:
            with open(new_file_path, 'rb') as f:
                file_data = f.read()
            
            checksum = self.checksum_manager.calculate_checksum(file_data)
            encrypted_data = self.encryption.encrypt_data(file_data)
            success = self.db.update_artefact(artefact_id, encrypted_data, checksum)
            
            if success:
                timestamp = datetime.now().isoformat()
                self._notify_observers(artefact_id, timestamp)
            
            return success
            
        except Exception as e:
            print(f"Error updating artefact: {e}")
            return False
    
    def delete_artefact(self, artefact_id, user):
        """deleting artefact - deleting in crud."""
        artefact = self.db.get_artefact(artefact_id)
        if not artefact:
            return False
        
        if not user.can_delete_artefact(artefact['owner_id']):
            print("Permission denied: You can only delete your own artefacts.")
            return False
        
        return self.db.delete_artefact(artefact_id)
    
    def list_user_artefacts(self, user):
        """getting all artefacts for user."""
        return self.db.get_user_artefacts(user.user_id)
    
    def list_all_artefacts(self, user):
        """getting all artefacts - admin only."""
        if user.role != 'admin':
            return []
        return self.db.get_all_artefacts()

