"""
user management module
handles users and permissions
uses inheritance - adminuser inherits from user
"""

import hashlib
from database import DatabaseManager

class User:
    """base user class - regular users."""
    
    def __init__(self, user_id, username, role):
        """create new user object."""
        # private variables (encapsulation)
        self._user_id = user_id
        self._username = username
        self._role = role
    
    # getter methods
    def get_user_id(self):
        """get user id."""
        return self._user_id
    
    def get_username(self):
        """get username."""
        return self._username
    
    def get_role(self):
        """get user role."""
        return self._role
    
    # properties for easier access
    @property
    def user_id(self):
        return self._user_id
    
    @property
    def username(self):
        return self._username
    
    @property
    def role(self):
        return self._role
    
    def can_view_artefact(self, artefact_owner_id):
        """checking if user can view , everyone can view"""
        return True
    
    def can_modify_artefact(self, artefact_owner_id):
        """checking if user can modify , only own artefacts"""
        return self._user_id == artefact_owner_id
    
    def can_delete_artefact(self, artefact_owner_id):
        """checking if user can delete , only own artefacts."""
        return self._user_id == artefact_owner_id

class AdminUser(User):
    """admin user class , inherits from user."""
    
    def can_modify_artefact(self, artefact_owner_id):
        """admin can modify any artefact."""
        return True
    
    def can_delete_artefact(self, artefact_owner_id):
        """admin can delete any artefact."""
        return True
    
    def can_delete_user(self):
        """admin can delete users."""
        return True

class UserManager:
    """manages users  registration, login, etc."""
    
    def __init__(self, db_manager):
        """initialize user manager."""
        self.db = db_manager
        # logged in user
        self.current_user = None  
    
    @staticmethod
    def hash_password(password):
        """hashing password before storing."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, role="user"):
        """register new user."""
        if role not in ['admin', 'user']:
            raise ValueError("role must be 'admin' or 'user'")
        
        # hashing password
        password_hash = self.hash_password(password)
        # adding to database
        user_id = self.db.create_user(username, password_hash, role)
        
        # return user object
        if role == 'admin':
            return AdminUser(user_id, username, role)
        else:
            return User(user_id, username, role)
    
    def login(self, username, password):
        """login user - check username and password."""
        # getting user from database
        user_data = self.db.get_user(username)
        if not user_data:
            # user not found
            return None  
        
        # hashing password and comparing
        password_hash = self.hash_password(password)
        if user_data['password_hash'] != password_hash:
            return None  # wrong password
        
        # creating and returning user object
        if user_data['role'] == 'admin':
            return AdminUser(user_data['user_id'], user_data['username'], user_data['role'])
        else:
            return User(user_data['user_id'], user_data['username'], user_data['role'])
    
    def get_current_user(self):
        """getting current logged in user."""
        return self.current_user
    
    def set_current_user(self, user):
        """setting current logged in user."""
        self.current_user = user
    
    def logout(self):
        """logout current user."""
        self.current_user = None

