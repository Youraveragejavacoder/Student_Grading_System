from datetime import date
from typing import List

from features.students.model import Student
from features.students.repository import StudentRepository

class StudentService:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def add_student(self, student_id: str, name: str) -> Student:
        student = Student(student_id=student_id, name=name)

        current_year = date.today().year
        if not student.student_id.endswith(f"-{current_year}"):
            raise ValueError(f"New student IDs must end with the current year ({current_year}).")

        if self.repository.get(student.student_id):
            raise ValueError(f"Student with ID '{student.student_id}' already exists.")

        self.repository.add(student)
        return student

    def get_student(self, student_id: str) -> Student:
        if not isinstance(student_id, str):
            raise TypeError("Student ID must be a string.")

        student = self.repository.get(student_id)
        if not student:
            raise KeyError(f"Student with ID '{student_id}' was not found.")
        return student

    def list_students(self) -> List[Student]:
        return self.repository.list_all()

    def update_student(self, student_id: str, name: str) -> Student:
        student = Student(student_id=student_id, name=name)

        if not self.repository.get(student.student_id):
            raise KeyError(f"Cannot update: Student with ID '{student.student_id}' does not exist.")

        self.repository.update(student)
        return student

    def remove_student(self, student_id: str) -> None:
        if not isinstance(student_id, str):
            raise TypeError("Student ID must be a string.")

        if not self.repository.get(student_id):
            raise KeyError(f"Cannot remove: Student with ID '{student_id}' does not exist.")

        self.repository.remove(student_id)
