import hashlib
from typing import Optional
from features.Auth.repository import AuthenticationRepository


class AuthenticationService:
    def __init__(self, database=None, repository: Optional[AuthenticationRepository] = None):
        self.repository = repository or AuthenticationRepository(database=database)
        self.current_user = None
        self.repository.ensure_admin(self._hash_password("Akiru123"))

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_teacher(self, name: str, username: str, password: str, confirm: str) -> bool:
        username = username.strip()
        name = name.strip()
        if not name:
            raise ValueError("Teacher name cannot be empty.")
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        self._validate_password(password, confirm)
        if username.casefold() == "admin":
            raise ValueError("That username is reserved for the administrator.")
        return self.repository.add_teacher(username, name, self._hash_password(password))

    def add_teacher(self, name: str, username: str, password: str, confirm: str) -> bool:
        self._require_admin()
        return self.register_teacher(name, username, password, confirm)

    def list_teachers(self) -> list[dict]:
        self._require_admin()
        return self.repository.list_by_role("teacher")

    def remove_teacher(self, teacher_id: int) -> None:
        self._require_admin()
        self.repository.remove_by_id_and_role(teacher_id, "teacher")

    @staticmethod
    def _validate_password(password: str, confirm: str) -> None:
        if not password:
            raise ValueError("Password cannot be empty.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        if password != confirm:
            raise ValueError("Passwords do not match.")

    def _require_admin(self) -> None:
        if not self.current_user or self.current_user.get("role") != "admin":
            raise PermissionError("Only the administrator can manage teacher accounts.")

    def authenticate(self, username: str, password: str) -> dict:
        username = username.strip()
        if not username or not password:
            raise ValueError("Please enter both username and password.")

        user_data = self.repository.find_by_username(username)
        if not user_data or user_data.get("role") not in {"admin", "teacher"}:
            raise ValueError("Invalid username or password.")

        hashed_input = self._hash_password(password)
        if user_data["password"] != hashed_input:
            raise ValueError("Invalid username or password.")

        self.current_user = user_data
        return user_data

    def authenticate_student(self, student_id: str, student_service) -> dict:
        student = student_service.get_student(student_id.strip())
        self.current_user = {
            "username": student.name,
            "role": "student",
            "student_id": student.student_id,
        }
        return self.current_user

    def logout(self):
        self.current_user = None
