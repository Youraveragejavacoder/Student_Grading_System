import hashlib
from typing import Optional
from features.Auth.repository import AuthenticationRepository


class AuthenticationService:
    def __init__(self, database=None, repository: Optional[AuthenticationRepository] = None):
        self.repository = repository or AuthenticationRepository(database=database)
        self.current_user = None

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register(self, username: str, password: str, confirm: str) -> bool:
        username = username.strip()

        if not username or not password:
            raise ValueError("Username and password cannot be empty.")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if password != confirm:
            raise ValueError("Passwords do not match.")

        hashed_pw = self._hash_password(password)
        return self.repository.add(username, hashed_pw)

    def authenticate(self, username: str, password: str) -> dict:
        username = username.strip()
        if not username or not password:
            raise ValueError("Please enter both username and password.")

        user_data = self.repository.find_by_username(username)
        if not user_data:
            raise ValueError("Invalid username or password.")

        hashed_input = self._hash_password(password)
        if user_data["password"] != hashed_input:
            raise ValueError("Invalid username or password.")

        self.current_user = user_data
        return user_data

    def logout(self):
        self.current_user = None