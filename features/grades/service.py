from typing import List, Union
from features.grades.model import Grade
from features.grades.repository import GradeRepository

class GradeService:
    def __init__(self, grade_repository: GradeRepository):
        self.repository = grade_repository

    def add_grade(self, student_id: str, subject: str, score: Union[int, float]) -> Grade:
        grade = Grade(student_id=student_id, subject=subject, score=score)

        if self.repository.get(grade.student_id, grade.subject):
            raise ValueError(
                f"Grade for subject '{grade.subject}' already exists for student '{grade.student_id}'."
            )

        self.repository.add(grade)
        return grade

    def view_grade(self, student_id: str, subject: str) -> Grade:
        if not isinstance(student_id, str) or not isinstance(subject, str):
            raise TypeError("Student ID and Subject must be strings.")

        grade = self.repository.get(student_id, subject)
        if not grade:
            raise KeyError(
                f"No grade found for subject '{subject}' for student ID '{student_id}'."
            )
        return grade

    def view_all_grades(self, student_id: str) -> List[Grade]:
        if not isinstance(student_id, str):
            raise TypeError("Student ID must be a string.")

        return self.repository.get_all_by_student(student_id)

    def update_grade(self, student_id: str, subject: str, new_score: Union[int, float]) -> Grade:
        grade = Grade(student_id=student_id, subject=subject, score=new_score)

        if not self.repository.get(grade.student_id, grade.subject):
            raise KeyError(
                f"Cannot update: No grade record exists for subject '{subject}' for student '{student_id}'."
            )

        self.repository.update(grade)
        return grade

    def remove_grade(self, student_id: str, subject: str) -> None:
        if not isinstance(student_id, str) or not isinstance(subject, str):
            raise TypeError("Student ID and Subject must be strings.")

        if not self.repository.get(student_id, subject):
            raise KeyError(
                f"Cannot remove: No grade record found for subject '{subject}' for student '{student_id}'."
            )

        self.repository.remove(student_id, subject)