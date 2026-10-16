import sqlite3
from pathlib import Path
from typing import Optional
from database.database import get_connection
from features.dashboard.model import DashboardStats, StudentGradeRow


class DashboardRepository:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path

    def get_stats(self) -> DashboardStats:
        try:
            kwargs = {"db_path": self.db_path} if self.db_path else {}
            with get_connection(**kwargs) as conn:
                students_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
                grades_count = conn.execute("SELECT COUNT(*) FROM grades").fetchone()[0]
                avg_score = conn.execute("SELECT AVG(score) FROM grades").fetchone()[0] or 0.0

                return DashboardStats(
                    total_students=students_count,
                    total_grades=grades_count,
                    average_score=round(float(avg_score), 2),
                )
        except sqlite3.Error:
            return DashboardStats(total_students=0, total_grades=0, average_score=0.0)

    def get_student_grade_overview(self) -> list[StudentGradeRow]:
        kwargs = {"db_path": self.db_path} if self.db_path else {}
        try:
            with get_connection(**kwargs) as conn:
                rows = conn.execute(
                    "SELECT s.student_id, s.name, g.subject, g.score "
                    "FROM students AS s "
                    "LEFT JOIN grades AS g ON g.student_id = s.student_id "
                    "ORDER BY s.name COLLATE NOCASE, g.subject COLLATE NOCASE"
                ).fetchall()
                return [
                    StudentGradeRow(
                        student_id=row["student_id"],
                        name=row["name"],
                        subject=row["subject"] or "No grades yet",
                        score=row["score"],
                    )
                    for row in rows
                ]
        except sqlite3.Error as err:
            raise RuntimeError(f"Could not load the student grade overview: {err}") from err
