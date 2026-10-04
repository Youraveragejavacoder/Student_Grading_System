import sqlite3
from typing import Optional, List
from pathlib import Path
from database.database import get_connection
from features.grades.model import Grade

class GradeRepository:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path
        self._initialize_table()

    def _initialize_table(self) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS grades (
                        student_id TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        score REAL NOT NULL,
                        PRIMARY KEY (student_id, subject),
                        FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
                    )
                """)
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not initialize grades storage: {err}") from err

    def add(self, grade: Grade) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute(
                    "INSERT INTO grades (student_id, subject, score) VALUES (?, ?, ?)",
                    (grade.student_id.strip(), grade.subject.strip(), float(grade.score))
                )
        except sqlite3.IntegrityError as err:
            raise ValueError(
                f"Could not add grade for '{grade.student_id}'. "
                "Make sure the student exists and the subject is not duplicated."
            ) from err
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not add grade: {err}") from err

    def get(self, student_id: str, subject: str) -> Optional[Grade]:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                cursor = conn.execute(
                    "SELECT student_id, subject, score FROM grades "
                    "WHERE student_id = ? AND subject = ?",
                    (student_id.strip(), subject.strip())
                )
                row = cursor.fetchone()
                if row:
                    return Grade(
                        student_id=row["student_id"],
                        subject=row["subject"],
                        score=row["score"]
                    )
                return None
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not read grades: {err}") from err

    def get_all_by_student(self, student_id: str) -> List[Grade]:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                cursor = conn.execute(
                    "SELECT student_id, subject, score "
                    "FROM grades WHERE student_id = ? ORDER BY subject",
                    (student_id.strip(),)
                )
                rows = cursor.fetchall()
                return [
                    Grade(student_id=row["student_id"], subject=row["subject"], score=row["score"])
                    for row in rows
                ]
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not list grades: {err}") from err

    def update(self, grade: Grade) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute(
                    "UPDATE grades SET score = ? WHERE student_id = ? AND subject = ?",
                    (float(grade.score), grade.student_id.strip(), grade.subject.strip())
                )
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not update grade: {err}") from err

    def remove(self, student_id: str, subject: str) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute(
                    "DELETE FROM grades WHERE student_id = ? AND subject = ?",
                    (student_id.strip(), subject.strip())
                )
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not remove grade: {err}") from err
