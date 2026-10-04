from dataclasses import dataclass
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


@dataclass
class RolePermissions:
    role: UserRole
    can_add_student: bool
    can_update_student: bool
    can_delete_student: bool
    can_add_grade: bool
    can_update_grade: bool
    can_delete_grade: bool


@dataclass
class DashboardStats:
    total_students: int
    total_grades: int
    average_score: float