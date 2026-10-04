from datetime import date

from PyQt6.QtCore import pyqtSignal, Qt
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
    QSizePolicy,
    QAbstractItemView,
)
from features.students.service import StudentService
from features.dashboard.toast import show_side_toast


class StudentsView(QWidget):
    student_deleted = pyqtSignal(str)

    def __init__(self, student_service: StudentService):
        super().__init__()
        self.student_service = student_service
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
        eyebrow = QLabel("DIRECTORY")
        eyebrow.setObjectName("eyebrowLabel")
        title = QLabel("Students")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Add, update, and find student records from one focused view.")
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

        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 17, 18, 17)
        form_layout.setSpacing(12)

        form_heading = QHBoxLayout()
        section_title = QLabel("Student details")
        section_title.setObjectName("sectionTitle")
        form_hint = QLabel("Create a new record or select a row to edit it.")
        form_hint.setObjectName("helperLabel")
        form_heading.addWidget(section_title)
        form_heading.addStretch()
        form_heading.addWidget(form_hint)
        form_layout.addLayout(form_heading)

        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(12)

        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText(f"00000-{date.today().year}")
        self.student_id_input.setMaxLength(10)
        self.student_id_input.setClearButtonEnabled(True)
        fields_layout.addWidget(self._field_block("Student ID", self.student_id_input), stretch=1)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full name")
        self.name_input.setClearButtonEnabled(True)
        fields_layout.addWidget(self._field_block("Full name", self.name_input), stretch=2)
        form_layout.addLayout(fields_layout)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        action_layout.addStretch()

        self.add_btn = QPushButton("Add student")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self._add_student)
        action_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Update")
        self.update_btn.setObjectName("secondaryButton")
        self.update_btn.clicked.connect(self._update_student)
        action_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete student")
        self.delete_btn.setObjectName("dangerButton")
        self.delete_btn.setToolTip("Permanently delete this student and their related grade records.")
        self.delete_btn.clicked.connect(self._delete_student)
        action_layout.addWidget(self.delete_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("ghostButton")
        clear_btn.setToolTip("Clear these form fields without changing saved records.")
        clear_btn.clicked.connect(self._clear_inputs)
        action_layout.addWidget(clear_btn)
        form_layout.addLayout(action_layout)
        layout.addWidget(form_card)

        toolbar_card = QFrame()
        toolbar_card.setObjectName("toolbarCard")
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(14, 12, 14, 12)
        toolbar_layout.setSpacing(10)

        search_label = QLabel("Find by student ID")
        search_label.setObjectName("fieldLabel")
        toolbar_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(f"Enter 00000-{date.today().year}")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.returnPressed.connect(self._search_student)
        toolbar_layout.addWidget(self.search_input, stretch=1)

        search_btn = QPushButton("Search")
        search_btn.setObjectName("secondaryButton")
        search_btn.clicked.connect(self._search_student)
        toolbar_layout.addWidget(search_btn)

        clear_search_btn = QPushButton("Show all")
        clear_search_btn.setObjectName("ghostButton")
        clear_search_btn.clicked.connect(self._clear_search)
        toolbar_layout.addWidget(clear_search_btn)
        layout.addWidget(toolbar_card)

        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(10)

        table_heading = QHBoxLayout()
        table_title = QLabel("Student directory")
        table_title.setObjectName("sectionTitle")
        table_hint = QLabel("Select a row to populate the form")
        table_hint.setObjectName("helperLabel")
        table_heading.addWidget(table_title)
        table_heading.addStretch()
        table_heading.addWidget(table_hint)
        table_layout.addLayout(table_heading)

        self.empty_label = QLabel("No student records loaded yet. Search for a student or add one above.")
        self.empty_label.setObjectName("emptyState")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.addWidget(self.empty_label)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Student ID", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(235)
        self.table.itemClicked.connect(self._on_table_click)
        table_layout.addWidget(self.table, stretch=1)
        layout.addWidget(table_card, stretch=1)

        self._update_empty_state()
        self._load_students()

    def _load_students(self):
        try:
            students = self.student_service.list_students()
            self.table.setRowCount(0)
            for student in students:
                self._add_row_to_table(student.student_id, student.name)
            self._update_empty_state()
        except RuntimeError as err:
            QMessageBox.critical(self, "Could not load students", str(err))

    def _add_student(self):
        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()

        try:
            student = self.student_service.add_student(student_id, name)
            self._upsert_row(student.student_id, student.name)
            self._clear_inputs()
            show_side_toast(self, "Student added", f"{student.name} was saved successfully.")
        except (ValueError, TypeError, RuntimeError) as err:
            QMessageBox.warning(self, "Could not add student", str(err))

    def _search_student(self):
        student_id = self.search_input.text().strip()
        if not student_id:
            QMessageBox.warning(self, "Search student", "Enter a Student ID to search.")
            return

        try:
            student = self.student_service.get_student(student_id)
            self.table.setRowCount(0)
            self._add_row_to_table(student.student_id, student.name)
        except (KeyError, TypeError, RuntimeError) as err:
            self.table.setRowCount(0)
            self._update_empty_state()
            QMessageBox.warning(self, "Student not found", str(err))

    def _clear_search(self):
        self.search_input.clear()
        self._load_students()

    def _update_student(self):
        student_id = self.student_id_input.text().strip()
        name = self.name_input.text().strip()

        try:
            student = self.student_service.update_student(student_id, name)
            self._upsert_row(student.student_id, student.name)
            self._clear_inputs()
            show_side_toast(self, "Student updated", f"{student.name}'s details were saved.")
        except (KeyError, ValueError, TypeError, RuntimeError) as err:
            QMessageBox.warning(self, "Could not update student", str(err))

    def _delete_student(self):
        student_id = self.student_id_input.text().strip()

        try:
            student = self.student_service.get_student(student_id)
            self.student_service.remove_student(student.student_id)
            row = self._find_row(student_id)
            if row >= 0:
                self.table.removeRow(row)
            self._clear_inputs()
            self._update_empty_state()
            self.student_deleted.emit(student.student_id)
            show_side_toast(
                self,
                "Student deleted",
                "The student and related grade records were permanently deleted.",
            )
        except (KeyError, TypeError, RuntimeError) as err:
            QMessageBox.warning(self, "Could not remove student", str(err))

    def _add_row_to_table(self, student_id: str, name: str):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        self.table.setItem(row_idx, 0, QTableWidgetItem(student_id))
        self.table.setItem(row_idx, 1, QTableWidgetItem(name))
        self._update_empty_state()

    def _upsert_row(self, student_id: str, name: str):
        row = self._find_row(student_id)
        if row < 0:
            self._add_row_to_table(student_id, name)
            return

        self.table.item(row, 1).setText(name)
        self._update_empty_state()

    def _find_row(self, student_id: str) -> int:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == student_id:
                return row
        return -1

    def _on_table_click(self, item):
        row = item.row()
        self.student_id_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())

    def _clear_inputs(self):
        self.student_id_input.clear()
        self.name_input.clear()

    def _update_empty_state(self):
        count = self.table.rowCount() if hasattr(self, "table") else 0
        self.record_count.setText(f"{count} record" + ("" if count == 1 else "s"))
        if hasattr(self, "empty_label"):
            self.empty_label.setVisible(count == 0)
