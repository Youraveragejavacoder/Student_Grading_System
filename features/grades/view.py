from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QMessageBox,
    QAbstractItemView,
)
from features.grades.service import GradeService
from features.dashboard.toast import show_side_toast


class GradesView(QWidget):
    def __init__(self, grade_service: GradeService):
        super().__init__()
        self.grade_service = grade_service
        self.setObjectName("pageSurface")
        self._init_ui()

    @staticmethod
    def _field_block(label_text: str, editor: QLineEdit) -> QWidget:
        wrapper = QWidget()
        field_layout = QVBoxLayout(wrapper)
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)

        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        field_layout.addWidget(label)
        field_layout.addWidget(editor)
        return wrapper

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        heading_layout = QVBoxLayout()
        heading_layout.setSpacing(4)
        eyebrow = QLabel("ACADEMIC RECORDS")
        eyebrow.setObjectName("eyebrowLabel")
        title = QLabel("Grades")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Load a student's gradebook, then add or adjust subject scores.")
        subtitle.setObjectName("pageSubtitle")
        heading_layout.addWidget(eyebrow)
        heading_layout.addWidget(title)
        heading_layout.addWidget(subtitle)

        self.record_count = QLabel("0 records")
        self.record_count.setObjectName("recordCount")

        header_layout.addLayout(heading_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.record_count, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header_layout)

        query_card = QFrame()
        query_card.setObjectName("toolbarCard")
        query_layout = QHBoxLayout(query_card)
        query_layout.setContentsMargins(14, 12, 14, 12)
        query_layout.setSpacing(10)

        query_label = QLabel("Student gradebook")
        query_label.setObjectName("fieldLabel")
        query_layout.addWidget(query_label)

        self.student_id_search = QLineEdit()
        self.student_id_search.setPlaceholderText(f"Enter student ID: 00000-{date.today().year}")
        self.student_id_search.setClearButtonEnabled(True)
        self.student_id_search.returnPressed.connect(self._load_grades)
        query_layout.addWidget(self.student_id_search, stretch=1)

        load_btn = QPushButton("Load grades")
        load_btn.setObjectName("primaryButton")
        load_btn.clicked.connect(self._load_grades)
        query_layout.addWidget(load_btn)
        layout.addWidget(query_card)

        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 17, 18, 17)
        form_layout.setSpacing(12)

        form_heading = QHBoxLayout()
        section_title = QLabel("Grade entry")
        section_title.setObjectName("sectionTitle")
        form_hint = QLabel("Select a table row to edit an existing score.")
        form_hint.setObjectName("helperLabel")
        form_heading.addWidget(section_title)
        form_heading.addStretch()
        form_heading.addWidget(form_hint)
        form_layout.addLayout(form_heading)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(12)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("e.g. Mathematics")
        self.subject_input.setClearButtonEnabled(True)
        fields_layout.addWidget(self._field_block("Subject", self.subject_input), stretch=2)

        self.score_input = QLineEdit()
        self.score_input.setPlaceholderText("0.00 – 100.00")
        self.score_input.setValidator(QDoubleValidator(0.0, 100.0, 2, self.score_input))
        self.score_input.setClearButtonEnabled(True)
        fields_layout.addWidget(self._field_block("Score", self.score_input), stretch=1)
        form_layout.addLayout(fields_layout)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        action_layout.addStretch()

        self.add_btn = QPushButton("Add grade")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self._add_grade)
        action_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Update")
        self.update_btn.setObjectName("secondaryButton")
        self.update_btn.clicked.connect(self._update_grade)
        action_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete grade")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.setToolTip("Permanently delete this grade record.")
        self.delete_btn.clicked.connect(self._delete_grade)
        action_layout.addWidget(self.delete_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("ghostButton")
        clear_btn.setToolTip("Clear these form fields without changing saved records.")
        clear_btn.clicked.connect(self._clear_grade_inputs)
        action_layout.addWidget(clear_btn)
        form_layout.addLayout(action_layout)
        layout.addWidget(form_card)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(10)

        table_heading = QHBoxLayout()
        table_title = QLabel("Grade records")
        table_title.setObjectName("sectionTitle")
        table_hint = QLabel("Click a row to edit")
        table_hint.setObjectName("helperLabel")
        table_heading.addWidget(table_title)
        table_heading.addStretch()
        table_heading.addWidget(table_hint)
        table_layout.addLayout(table_heading)

        self.empty_label = QLabel("No grades loaded. Enter a student ID above to view the gradebook.")
        self.empty_label.setObjectName("emptyState")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.addWidget(self.empty_label)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Student ID", "Subject", "Score"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(220)
        self.table.itemClicked.connect(self._on_table_click)
        table_layout.addWidget(self.table, stretch=1)
        layout.addWidget(table_card, stretch=1)

        self._update_empty_state()

    def _load_grades(self):
        student_id = self.student_id_search.text().strip()
        if not student_id:
            QMessageBox.warning(self, "Load grades", "Enter a Student ID to query.")
            return

        self._populate_grades(student_id)

    def _populate_grades(self, student_id: str):
        try:
            grades = self.grade_service.view_all_grades(student_id)
            self.table.setRowCount(0)
            for grade in grades:
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(grade.student_id))
                self.table.setItem(row_idx, 1, QTableWidgetItem(grade.subject))
                self.table.setItem(row_idx, 2, QTableWidgetItem(f"{grade.score:.2f}"))
            self._update_empty_state()
        except (KeyError, TypeError, ValueError) as err:
            QMessageBox.warning(self, "Could not load grades", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Database error", str(err))

    def _add_grade(self):
        student_id = self.student_id_search.text().strip()
        subject = self.subject_input.text().strip()
        score_raw = self.score_input.text().strip()

        try:
            score = float(score_raw)
            self.grade_service.add_grade(student_id, subject, score)
            self._populate_grades(student_id)
            self._clear_grade_inputs()
            show_side_toast(self, "Grade added", f"{subject} was saved successfully.")
        except ValueError as err:
            QMessageBox.warning(self, "Could not add grade", str(err))
        except (TypeError, KeyError) as err:
            QMessageBox.warning(self, "Could not add grade", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Database error", str(err))

    def _update_grade(self):
        student_id = self.student_id_search.text().strip()
        subject = self.subject_input.text().strip()
        score_raw = self.score_input.text().strip()

        try:
            score = float(score_raw)
            self.grade_service.update_grade(student_id, subject, score)
            self._populate_grades(student_id)
            self._clear_grade_inputs()
            show_side_toast(self, "Grade updated", f"{subject} was updated successfully.")
        except (ValueError, TypeError, KeyError) as err:
            QMessageBox.warning(self, "Could not update grade", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Database error", str(err))

    def _delete_grade(self):
        student_id = self.student_id_search.text().strip()
        subject = self.subject_input.text().strip()

        try:
            grade = self.grade_service.view_grade(student_id, subject)
            self.grade_service.remove_grade(grade.student_id, grade.subject)
            self._populate_grades(student_id)
            self._clear_grade_inputs()
            show_side_toast(
                self,
                "Grade deleted",
                f"{grade.subject} was permanently deleted.",
            )
        except (ValueError, TypeError, KeyError) as err:
            QMessageBox.warning(self, "Could not remove grade", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Database error", str(err))

    def _on_table_click(self, item):
        row = item.row()
        self.student_id_search.setText(self.table.item(row, 0).text())
        self.subject_input.setText(self.table.item(row, 1).text())
        self.score_input.setText(self.table.item(row, 2).text())

    def clear_student(self, student_id: str):
        matching_rows = [
            row
            for row in range(self.table.rowCount())
            if self.table.item(row, 0) and self.table.item(row, 0).text() == student_id
        ]
        for row in reversed(matching_rows):
            self.table.removeRow(row)

        if self.student_id_search.text().strip() == student_id:
            self.student_id_search.clear()
            self._clear_grade_inputs()

        self._update_empty_state()

    def _clear_grade_inputs(self):
        self.subject_input.clear()
        self.score_input.clear()

    def _update_empty_state(self):
        count = self.table.rowCount() if hasattr(self, "table") else 0
        self.record_count.setText(f"{count} record" + ("" if count == 1 else "s"))
        if hasattr(self, "empty_label"):
            self.empty_label.setVisible(count == 0)
