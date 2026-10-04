import sqlite3
from typing import List, Optional
from pathlib import Path
from database.database import get_connection
from features.students.model import Student

class StudentRepository:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path
        self._initialize_table()

    def _initialize_table(self) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        student_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL
                    )
                """)
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not initialize students storage: {err}") from err

    def add(self, student: Student) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute(
                    "INSERT INTO students (student_id, name) VALUES (?, ?)",
                    (student.student_id.strip(), student.name.strip())
                )
        except sqlite3.IntegrityError as err:
            raise ValueError(f"Student with ID '{student.student_id}' already exists.") from err
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not add student: {err}") from err

    def get(self, student_id: str) -> Optional[Student]:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                cursor = conn.execute(
                    "SELECT student_id, name FROM students WHERE student_id = ?",
                    (student_id.strip(),)
                )
                row = cursor.fetchone()
                if row:
                    return Student(student_id=row["student_id"], name=row["name"])
                return None
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not read students: {err}") from err

    def list_all(self) -> List[Student]:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                rows = conn.execute(
                    "SELECT student_id, name FROM students ORDER BY student_id"
                ).fetchall()
                return [
                    Student(student_id=row["student_id"], name=row["name"])
                    for row in rows
                ]
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not list students: {err}") from err

    def update(self, student: Student) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute(
                    "UPDATE students SET name = ? WHERE student_id = ?",
                    (student.name.strip(), student.student_id.strip())
                )
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not update student: {err}") from err

    def remove(self, student_id: str) -> None:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                conn.execute(
                    "DELETE FROM grades WHERE student_id = ?",
                    (student_id.strip(),)
                )
                conn.execute(
                    "DELETE FROM students WHERE student_id = ?",
                    (student_id.strip(),)
                )
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not remove student: {err}") from err
