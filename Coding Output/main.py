"""
secure music copyright application
main application file
uses singleton, factory, strategy, observer, inheritance patterns
"""

import os
import sys
from database import DatabaseManager
from encryption import EncryptionManager
from user_manager import UserManager, User
from artefact_manager import ArtefactManager, TimestampObserver

class MusicCopyrightApp:
    """main application class , coordinates everything."""
    
    def __init__(self):
        """initialize application."""
        # singleton , only one database connection
        self.db = DatabaseManager()
        # factory , creates encryption
        self.encryption = EncryptionManager()
        # set up encryption key
        master_password = "secure_master_key_2025"
        self.encryption.derive_key_from_password(master_password)
        
        # creating managers
        self.user_manager = UserManager(self.db)
        self.artefact_manager = ArtefactManager(self.db, self.encryption)
        
        # observering , for timestamps
        timestamp_observer = TimestampObserver(self.db)
        self.artefact_manager.add_observer(timestamp_observer)
        
        # creating output folder
        if not os.path.exists("output"):
            os.makedirs("output")
    
    def display_menu(self):
        """displaying main menu."""
        print("\n" + "="*60)
        print("Secure Music Copyright Application")
        print("="*60)
        if self.user_manager.current_user:
            print(f"Logged in as: {self.user_manager.current_user.username} "
                  f"({self.user_manager.current_user.role})")
        print("\nMain Menu:")
        print("1. Register new user")
        print("2. Login")
        print("3. Logout")
        print("4. Create artefact (Upload file)")
        print("5. View artefact")
        print("6. List my artefacts")
        print("7. Update artefact")
        print("8. Delete artefact")
        if self.user_manager.current_user and self.user_manager.current_user.role == 'admin':
            print("9. List all artefacts (Admin)")
            print("10. Delete user (Admin)")
        print("0. Exit")
        print("="*60)
    
    def register_user(self):
        """handling user registration."""
        print("\n--- User Registration ---")
        username = input("Enter username: ").strip()
        if not username:
            print("Username cannot be empty.")
            return
        
        password = input("Enter password: ").strip()
        if not password:
            print("Password cannot be empty.")
            return
        
        role = input("Enter role (admin/user) [default: user]: ").strip().lower()
        if not role:
            role = "user"
        
        try:
            user = self.user_manager.register_user(username, password, role)
            print(f"User '{username}' registered successfully as {role}.")
        except ValueError as e:
            print(f"Registration failed: {e}")
    
    def login(self):
        """handling user login."""
        print("\n--- Login ---")
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        
        user = self.user_manager.login(username, password)
        if user:
            self.user_manager.set_current_user(user)
            print(f"Login successful! Welcome, {username}.")
        else:
            print("Login failed: Invalid username or password.")
    
    def logout(self):
        """handling user logout."""
        if self.user_manager.current_user:
            username = self.user_manager.current_user.username
            self.user_manager.logout()
            print(f"Logged out successfully. Goodbye, {username}!")
        else:
            print("No user is currently logged in.")
    
    def create_artefact(self):
        """creating new artefact , create in crud."""
        if not self.user_manager.current_user:
            print("Please login first.")
            return
        
        print("\n--- Create Artefact ---")
        file_path = input("Enter file path: ").strip()
        artefact_name = input("Enter artefact name: ").strip()
        
        print("Artefact types: lyrics, score, audio")
        artefact_type = input("Enter artefact type: ").strip().lower()
        
        if artefact_type not in ['lyrics', 'score', 'audio']:
            print("Invalid artefact type. Must be 'lyrics', 'score', or 'audio'.")
            return
        
        try:
            artefact_id = self.artefact_manager.create_artefact(
                self.user_manager.current_user,
                file_path,
                artefact_name,
                artefact_type
            )
            if artefact_id:
                print(f"Artefact created successfully! ID: {artefact_id}")
            else:
                print("Failed to create artefact.")
        except Exception as e:
            print(f"Error: {e}")
    
    def view_artefact(self):
        """view artefact - read in crud."""
        if not self.user_manager.current_user:
            print("Please login first.")
            return
        
        print("\n--- View Artefact ---")
        try:
            artefact_id = int(input("Enter artefact ID: ").strip())
        except ValueError:
            print("Invalid artefact ID.")
            return
        
        artefact = self.artefact_manager.read_artefact(
            artefact_id,
            self.user_manager.current_user
        )
        
        if artefact:
            print("\nArtefact Information:")
            print(f"  ID: {artefact['artefact_id']}")
            print(f"  Name: {artefact['artefact_name']}")
            print(f"  Type: {artefact['artefact_type']}")
            print(f"  Created: {artefact['created_at']}")
            print(f"  Modified: {artefact.get('modified_at', 'Never')}")
            print(f"  Checksum: {artefact['checksum'][:16]}...")
            
            download = input("\nDownload decrypted file? (y/n): ").strip().lower()
            if download == 'y':
                output_path = f"output/artefact_{artefact_id}_{artefact['artefact_name']}"
                data = self.artefact_manager.get_artefact_data(
                    artefact_id,
                    self.user_manager.current_user,
                    output_path
                )
                if data:
                    print(f"File decrypted and saved to: {output_path}")
                else:
                    print("Failed to retrieve artefact data.")
        else:
            print("Artefact not found or access denied.")
    
    def list_artefacts(self):
        """list user's artefacts."""
        if not self.user_manager.current_user:
            print("Please login first.")
            return
        
        print("\n--- My Artefacts ---")
        artefacts = self.artefact_manager.list_user_artefacts(
            self.user_manager.current_user
        )
        
        if artefacts:
            print(f"\nFound {len(artefacts)} artefact(s):\n")
            for artefact in artefacts:
                print(f"  ID: {artefact['artefact_id']}")
                print(f"  Name: {artefact['artefact_name']}")
                print(f"  Type: {artefact['artefact_type']}")
                print(f"  Created: {artefact['created_at']}")
                print(f"  Modified: {artefact.get('modified_at', 'Never')}")
                print("-" * 40)
        else:
            print("No artefacts found.")
    
    def update_artefact(self):
        """update artefact - update in crud."""
        if not self.user_manager.current_user:
            print("Please login first.")
            return
        
        print("\n--- Update Artefact ---")
        try:
            artefact_id = int(input("Enter artefact ID to update: ").strip())
        except ValueError:
            print("Invalid artefact ID.")
            return
        
        new_file_path = input("Enter path to new file: ").strip()
        
        try:
            success = self.artefact_manager.update_artefact(
                artefact_id,
                new_file_path,
                self.user_manager.current_user
            )
            if success:
                print("Artefact updated successfully!")
            else:
                print("Failed to update artefact.")
        except Exception as e:
            print(f"Error: {e}")
    
    def delete_artefact(self):
        """delete artefact - delete in crud."""
        if not self.user_manager.current_user:
            print("Please login first.")
            return
        
        print("\n--- Delete Artefact ---")
        try:
            artefact_id = int(input("Enter artefact ID to delete: ").strip())
        except ValueError:
            print("Invalid artefact ID.")
            return
        
        confirm = input("Are you sure you want to delete this artefact? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Deletion cancelled.")
            return
        
        success = self.artefact_manager.delete_artefact(
            artefact_id,
            self.user_manager.current_user
        )
        
        if success:
            print("Artefact deleted successfully.")
        else:
            print("Failed to delete artefact (not found or permission denied).")
    
    def list_all_artefacts(self):
        """list all artefacts - admin only."""
        if not self.user_manager.current_user:
            print("Please login first.")
            return
        
        if self.user_manager.current_user.role != 'admin':
            print("Access denied: Admin privileges required.")
            return
        
        print("\n--- All Artefacts (Admin View) ---")
        artefacts = self.artefact_manager.list_all_artefacts(
            self.user_manager.current_user
        )
        
        if artefacts:
            print(f"\nFound {len(artefacts)} artefact(s):\n")
            for artefact in artefacts:
                print(f"  ID: {artefact['artefact_id']}")
                print(f"  Name: {artefact['artefact_name']}")
                print(f"  Type: {artefact['artefact_type']}")
                print(f"  Owner: {artefact.get('owner_username', 'Unknown')}")
                print(f"  Created: {artefact['created_at']}")
                print("-" * 40)
        else:
            print("No artefacts found.")
    
    def delete_user(self):
        """delete user - admin only."""
        if not self.user_manager.current_user:
            print("Please login first.")
            return
        
        if self.user_manager.current_user.role != 'admin':
            print("Access denied: Admin privileges required.")
            return
        
        print("\n--- Delete User (Admin) ---")
        username = input("Enter username to delete: ").strip()
        
        user_data = self.db.get_user(username)
        if not user_data:
            print("User not found.")
            return
        
        confirm = input(f"Are you sure you want to delete user '{username}'? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Deletion cancelled.")
            return
        
        success = self.db.delete_user(user_data['user_id'])
        if success:
            print(f"User '{username}' and all their artefacts deleted successfully.")
        else:
            print("Failed to delete user.")
    
    def run(self):
        """main application loop."""
        print("Welcome to the Secure Music Copyright Application!")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '0':
                print("Thank you for using the Secure Music Copyright Application!")
                break
            elif choice == '1':
                self.register_user()
            elif choice == '2':
                self.login()
            elif choice == '3':
                self.logout()
            elif choice == '4':
                self.create_artefact()
            elif choice == '5':
                self.view_artefact()
            elif choice == '6':
                self.list_artefacts()
            elif choice == '7':
                self.update_artefact()
            elif choice == '8':
                self.delete_artefact()
            elif choice == '9' and self.user_manager.current_user and self.user_manager.current_user.role == 'admin':
                self.list_all_artefacts()
            elif choice == '10' and self.user_manager.current_user and self.user_manager.current_user.role == 'admin':
                self.delete_user()
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

def main():
    """main entry point."""
    try:
        app = MusicCopyrightApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
    finally:
        db = DatabaseManager()
        db.close()

if __name__ == "__main__":
    main()

