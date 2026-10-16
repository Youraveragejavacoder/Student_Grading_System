from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from features.grades.service import GradeService


class StudentPortal(QWidget):
    def __init__(self, grade_service: GradeService):
        super().__init__()
        self.grade_service = grade_service
        self.setObjectName("pageSurface")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(18)

        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        eyebrow = QLabel("STUDENT PORTAL")
        eyebrow.setObjectName("eyebrowLabel")
        self.name_label = QLabel("My gradebook")
        self.name_label.setObjectName("pageTitle")
        self.id_label = QLabel("Sign in with your Student ID to view your grades.")
        self.id_label.setObjectName("pageSubtitle")
        title_layout.addWidget(eyebrow)
        title_layout.addWidget(self.name_label)
        title_layout.addWidget(self.id_label)
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)

        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        self.subject_count = self._metric("SUBJECTS", "0")
        self.average = self._metric("AVERAGE", "--")
        self.highest = self._metric("HIGHEST SCORE", "--")
        for metric in (self.subject_count, self.average, self.highest):
            metrics.addWidget(metric["frame"])
        layout.addLayout(metrics)

        table_frame = QFrame()
        table_frame.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(10)

        table_header = QHBoxLayout()
        table_title = QLabel("My grades")
        table_title.setObjectName("sectionTitle")
        table_header.addWidget(table_title)
        table_header.addStretch()
        self.record_count = QLabel("0 records")
        self.record_count.setObjectName("recordCount")
        table_header.addWidget(self.record_count)
        table_layout.addLayout(table_header)

        self.empty_state = QLabel("No grades have been recorded for your account yet.")
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.addWidget(self.empty_state)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Subject", "Score"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(260)
        table_layout.addWidget(self.table, stretch=1)
        layout.addWidget(table_frame, stretch=1)

    @staticmethod
    def _metric(title: str, value: str) -> dict:
        frame = QFrame()
        frame.setObjectName("statCard")
        metric_layout = QVBoxLayout(frame)
        metric_layout.setContentsMargins(17, 15, 17, 15)
        metric_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("studentPortalMetric")
        value_label = QLabel(value)
        value_label.setObjectName("pageTitle")
        metric_layout.addWidget(title_label)
        metric_layout.addWidget(value_label)
        return {"frame": frame, "value_label": value_label}

    def load_student(self, user: dict) -> None:
        student_id = user.get("student_id", "")
        self.name_label.setText(user.get("username", "My gradebook"))
        self.id_label.setText(f"Student ID: {student_id}")

        grades = self.grade_service.view_all_grades(student_id)
        self.table.setRowCount(0)
        scores = []
        for grade in grades:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(grade.subject))
            self.table.setItem(row, 1, QTableWidgetItem(f"{grade.score:.2f}%"))
            scores.append(float(grade.score))

        count = len(grades)
        self.record_count.setText(f"{count} record" + ("" if count == 1 else "s"))
        self.subject_count["value_label"].setText(str(count))
        self.average["value_label"].setText(
            f"{sum(scores) / count:.2f}%" if count else "--"
        )
        self.highest["value_label"].setText(f"{max(scores):.2f}%" if scores else "--")
        self.empty_state.setVisible(count == 0)
