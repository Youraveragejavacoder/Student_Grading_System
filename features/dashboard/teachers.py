from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QAbstractItemView,
)
from features.Auth.service import AuthenticationService


class TeacherAccountsView(QWidget):
    def __init__(self, auth_service: AuthenticationService):
        super().__init__()
        self.auth_service = auth_service
        self.setObjectName("pageSurface")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(16)

        title = QLabel("Teacher accounts")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Create and manage staff access for the teaching workspace.")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        form = QFrame()
        form.setObjectName("formCard")
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(18, 16, 18, 16)
        form_layout.setSpacing(10)

        fields = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Teacher full name")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Teacher username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Temporary password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        fields.addWidget(self.name_input, stretch=1)
        fields.addWidget(self.username_input, stretch=1)
        fields.addWidget(self.password_input, stretch=1)
        fields.addWidget(self.confirm_input, stretch=1)
        form_layout.addLayout(fields)

        actions = QHBoxLayout()
        actions.addStretch()
        self.add_button = QPushButton("Create teacher account")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setMinimumSize(220, 42)
        self.add_button.clicked.connect(self._add_teacher)
        actions.addWidget(self.add_button)
        form_layout.addLayout(actions)
        layout.addWidget(form)

        table_frame = QFrame()
        table_frame.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(10)

        table_heading = QHBoxLayout()
        heading = QLabel("Active teacher accounts")
        heading.setObjectName("sectionTitle")
        self.count_label = QLabel("0 accounts")
        self.count_label.setObjectName("recordCount")
        table_heading.addWidget(heading)
        table_heading.addStretch()
        table_heading.addWidget(self.count_label)
        table_layout.addLayout(table_heading)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Teacher", "Username", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        table_layout.addWidget(self.table, stretch=1)
        layout.addWidget(table_frame, stretch=1)

    def refresh(self):
        try:
            teachers = self.auth_service.list_teachers()
            self.table.setRowCount(0)
            for teacher in teachers:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(teacher.get("name") or teacher["username"]))
                self.table.setItem(row, 1, QTableWidgetItem(teacher["username"]))
                remove_button = QPushButton("Remove")
                remove_button.setObjectName("dangerButton")
                remove_button.setMinimumSize(104, 36)
                remove_button.setToolTip("Remove this teacher's account access.")
                remove_button.clicked.connect(
                    lambda checked=False, teacher_id=teacher["id"]: self._remove_teacher(teacher_id)
                )
                self.table.setCellWidget(row, 2, remove_button)
            count = len(teachers)
            self.count_label.setText(f"{count} account" + ("" if count == 1 else "s"))
        except (PermissionError, RuntimeError) as err:
            QMessageBox.critical(self, "Could not load teacher accounts", str(err))

    def _add_teacher(self):
        try:
            self.auth_service.add_teacher(
                self.name_input.text(),
                self.username_input.text(),
                self.password_input.text(),
                self.confirm_input.text(),
            )
            self.name_input.clear()
            self.username_input.clear()
            self.password_input.clear()
            self.confirm_input.clear()
            self.refresh()
        except (ValueError, TypeError, PermissionError, RuntimeError) as err:
            QMessageBox.warning(self, "Could not create teacher account", str(err))

    def _remove_teacher(self, teacher_id: int):
        answer = QMessageBox.question(
            self,
            "Remove teacher account",
            "Remove this teacher's access to the system?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.auth_service.remove_teacher(teacher_id)
            self.refresh()
        except (PermissionError, RuntimeError) as err:
            QMessageBox.warning(self, "Could not remove teacher", str(err))
