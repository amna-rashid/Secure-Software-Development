"""
Automated Test Script for Secure Music Copyright Application
=============================================================
This script tests the core functionality of the application
without requiring manual user input.
"""

import os
import sys
from database import DatabaseManager
from encryption import EncryptionManager
from checksum import ChecksumManager
from user_manager import UserManager
from artefact_manager import ArtefactManager, TimestampObserver

def test_database():
    """test database operations."""
    print("=" * 60)
    print("Testing Database Module (Singleton Pattern)")
    print("=" * 60)
    
    # testing singleton pattern , should get same instance
    db1 = DatabaseManager()
    db2 = DatabaseManager()
    assert db1 is db2, "Singleton pattern failed - different instances created"
    print("Singleton pattern working: Same instance returned")
    
    # testing user creation
    try:
        user_id = db1.create_user("testuser", "hashed_password", "user")
        print(f" User created successfully: ID {user_id}")
        
        # testing user retrieval
        user = db1.get_user("testuser")
        assert user is not None, "User not found"
        assert user['username'] == "testuser", "Username mismatch"
        print("User retrieval working")
        
        # cleaning up
        db1.delete_user(user_id)
        print("User deletion working")
    except Exception as e:
        print(f"Database test failed: {e}")
        return False
    
    return True

def test_encryption():
    """Test encryption operations."""
    print("\n" + "=" * 60)
    print("Testing Encryption Module (Factory & Strategy Patterns)")
    print("=" * 60)
    
    try:
        # testing factory pattern
        encryption = EncryptionManager()
        encryption.generate_key()
        print(" Encryption manager created (Factory pattern)")
        
        # testing encryption/decryption
        test_data = b"This is test data for encryption"
        encrypted = encryption.encrypt_data(test_data)
        print(" Data encrypted successfully")
        
        decrypted = encryption.decrypt_data(encrypted)
        assert decrypted == test_data, "Decryption failed - data mismatch"
        print(" Data decrypted successfully - integrity verified")
        
        # testing password-based key derivation
        encryption.derive_key_from_password("test_password")
        encrypted2 = encryption.encrypt_data(test_data)
        decrypted2 = encryption.decrypt_data(encrypted2)
        assert decrypted2 == test_data, "Password-based encryption failed"
        print(" Password-based key derivation working")
        
    except Exception as e:
        print(f" Encryption test failed: {e}")
        return False
    
    return True

def test_checksum():
    """test checksum operations."""
    print("\n" + "=" * 60)
    print("Testing Checksum Module")
    print("=" * 60)
    
    try:
        test_data = b"This is test data for checksum"
        checksum = ChecksumManager.calculate_checksum(test_data)
        print(f" Checksum calculated: {checksum[:16]}...")
        
        # testing verification
        is_valid = ChecksumManager.verify_checksum(test_data, checksum)
        assert is_valid, "Checksum verification failed"
        print("Checksum verification working")
        
        # testing with modified data
        modified_data = b"This is modified data"
        is_valid_modified = ChecksumManager.verify_checksum(modified_data, checksum)
        assert not is_valid_modified, "Checksum should fail for modified data"
        print("Checksum detects tampering correctly")
        
    except Exception as e:
        print(f" Checksum test failed: {e}")
        return False
    
    return True

def test_user_manager():
    """testing user management."""
    print("\n" + "=" * 60)
    print("Testing User Manager (Inheritance Pattern)")
    print("=" * 60)
    
    try:
        db = DatabaseManager()
        user_mgr = UserManager(db)
        
        # testing user registration
        user = user_mgr.register_user("testuser2", "password123", "user")
        print("User registered successfully")
        
        # testing login
        logged_user = user_mgr.login("testuser2", "password123")
        assert logged_user is not None, "Login failed"
        assert logged_user.username == "testuser2", "Username mismatch"
        print(" Login working")
        
        # testing inheritance , regular user
        assert not user.can_delete_artefact(999), "Regular user should not delete others' artefacts"
        print(" Regular user permissions working")
        
        # testing admin user
        admin = user_mgr.register_user("admin_test", "admin123", "admin")
        assert admin.role == "admin", "Admin role not set"
        assert admin.can_delete_artefact(999), "Admin should delete any artefact"
        print(" Admin user permissions working (Inheritance pattern)")
        
        # cleaning up
        db.delete_user(user.user_id)
        db.delete_user(admin.user_id)
        print(" Cleanup successful")
        
    except Exception as e:
        print(f" User manager test failed: {e}")
        return False
    
    return True

def test_artefact_manager():
    """testig artefact CRUD operations."""
    print("\n" + "=" * 60)
    print("Testing Artefact Manager (CRUD & Observer Pattern)")
    print("=" * 60)
    
    try:
        # setup
        db = DatabaseManager()
        encryption = EncryptionManager()
        encryption.derive_key_from_password("test_master_key")
        artefact_mgr = ArtefactManager(db, encryption)
        
        # adding observer
        observer = TimestampObserver(db)
        artefact_mgr.add_observer(observer)
        print(" Observer pattern implemented")
        
        # creating test user
        user_mgr = UserManager(db)
        user = user_mgr.register_user("artefact_user", "pass123", "user")
        
        # creating test file
        test_file = "test_artefact.txt"
        with open(test_file, 'w') as f:
            f.write("This is a test artefact file")
        
        # creating operation
        artefact_id = artefact_mgr.create_artefact(
            user, test_file, "Test Artefact", "lyrics"
        )
        assert artefact_id is not None, "Artefact creation failed"
        print(f" CREATE operation working: Artefact ID {artefact_id}")
        
        # READ operation
        artefact = artefact_mgr.read_artefact(artefact_id, user)
        assert artefact is not None, "Artefact read failed"
        assert artefact['artefact_name'] == "Test Artefact", "Artefact name mismatch"
        print(" READ operation working")
        
        # UPDATE operation
        with open(test_file, 'w') as f:
            f.write("This is updated test artefact file")
        
        updated = artefact_mgr.update_artefact(artefact_id, test_file, user)
        assert updated, "Artefact update failed"
        print(" UPDATE operation working")
        
        # verifing checksum changed
        updated_artefact = artefact_mgr.read_artefact(artefact_id, user)
        assert updated_artefact['modified_at'] is not None, "Modification timestamp not set"
        print(" Timestamp recording working (Observer pattern)")
        
        # DELETE operation
        deleted = artefact_mgr.delete_artefact(artefact_id, user)
        assert deleted, "Artefact deletion failed"
        print(" DELETE operation working")
        
        # clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        db.delete_user(user.user_id)
        print(" Cleanup successful")
        
    except Exception as e:
        print(f" Artefact manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_integration():
    """Test full integration workflow."""
    print("\n" + "=" * 60)
    print("Testing Full Integration Workflow")
    print("=" * 60)
    
    try:
        # initializing all components
        db = DatabaseManager()
        encryption = EncryptionManager()
        encryption.derive_key_from_password("master_key_2025")
        user_mgr = UserManager(db)
        artefact_mgr = ArtefactManager(db, encryption)
        
        # creating admin user
        admin = user_mgr.register_user("admin_integration", "admin_pass", "admin")
        user_mgr.set_current_user(admin)
        print(" Admin user created and logged in")
        
        # creating regular user
        regular_user = user_mgr.register_user("user_integration", "user_pass", "user")
        print(" Regular user created")
        
        # creating test file
        test_file = "integration_test.txt"
        with open(test_file, 'w') as f:
            f.write("Integration test file content")
        
        # uploading artefact as regular user
        artefact_id = artefact_mgr.create_artefact(
            regular_user, test_file, "Integration Test", "lyrics"
        )
        print(f" Artefact uploaded: ID {artefact_id}")
        
        # admin views all artefacts
        all_artefacts = artefact_mgr.list_all_artefacts(admin)
        assert len(all_artefacts) > 0, "Admin should see all artefacts"
        print(" Admin can view all artefacts")
        
        # regular user views own artefacts
        user_artefacts = artefact_mgr.list_user_artefacts(regular_user)
        assert len(user_artefacts) > 0, "User should see own artefacts"
        print(" User can view own artefacts")
        
        # testing permission , user cannot modify others artefacts
        other_user = user_mgr.register_user("other_user", "pass", "user")
        can_modify = other_user.can_modify_artefact(regular_user.user_id)
        assert not can_modify, "User should not modify others' artefacts"
        print(" Permission control working")
        
        # clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        db.delete_user(admin.user_id)
        db.delete_user(regular_user.user_id)
        db.delete_user(other_user.user_id)
        print(" Integration test cleanup successful")
        
    except Exception as e:
        print(f" Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """run all tests."""
    print("\n" + "=" * 60)
    print("SECURE MUSIC COPYRIGHT APPLICATION - AUTOMATED TESTS")
    print("=" * 60)
    
    results = []
    
    # running all tests
    results.append(("Database", test_database()))
    results.append(("Encryption", test_encryption()))
    results.append(("Checksum", test_checksum()))
    results.append(("User Manager", test_user_manager()))
    results.append(("Artefact Manager", test_artefact_manager()))
    results.append(("Integration", test_integration()))
    
    # printing summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = " PASSED" if result else "FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    # cleaning up database file if all tests passed
    if passed == total:
        try:
            if os.path.exists("music_copyright.db"):
                os.remove("music_copyright.db")
                print("\n Test database cleaned up")
        except:
            pass
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



