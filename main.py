import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

from database.database import Database

from features.students.repository import StudentRepository
from features.students.service import StudentService
from features.grades.repository import GradeRepository
from features.grades.service import GradeService
from features.Auth.repository import AuthenticationRepository
from features.Auth.service import AuthenticationService

from features.dashboard.repository import DashboardRepository
from features.dashboard.service import UIService
from features.dashboard.view import GradingSystemUI


def log_uncaught_exceptions(exctype, value, tb):
    sys.__excepthook__(exctype, value, tb)


sys.excepthook = log_uncaught_exceptions


def load_stylesheet(app: QApplication) -> None:
    base_dir = Path(__file__).parent
    candidates = [
        base_dir / "style.qss",
        base_dir / "features" / "dashboard" / "style.qss",
        base_dir / "features" / "ui" / "style.qss",
    ]

    loaded = False
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            print(f"[QSS] Successfully loaded stylesheet from: {path.resolve()}")
            loaded = True
            break

    if not loaded:
        print("[QSS WARNING] Could not find style.qss! Check file location.")


def main():
    app = QApplication(sys.argv)
    load_stylesheet(app)

    db = Database()

    student_repo = StudentRepository(db_path=db.db_path)
    grade_repo = GradeRepository(db_path=db.db_path)
    auth_repo = AuthenticationRepository(database=db)
    dashboard_repo = DashboardRepository(db_path=db.db_path)

    student_service = StudentService(student_repo)
    grade_service = GradeService(grade_repo)
    auth_service = AuthenticationService(repository=auth_repo)
    ui_service = UIService(dashboard_repo)

    window = GradingSystemUI(
        student_service=student_service,
        grade_service=grade_service,
        auth_service=auth_service,
        ui_service=ui_service,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
