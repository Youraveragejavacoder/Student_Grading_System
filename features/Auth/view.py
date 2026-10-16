from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QMessageBox,
    QSizePolicy,
)
from features.Auth.service import AuthenticationService
from features.students.service import StudentService


def _build_brand_panel() -> QFrame:
    panel = QFrame()
    panel.setObjectName("authBrandPanel")
    panel.setMinimumWidth(330)
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(42, 42, 42, 42)
    layout.setSpacing(10)

    kicker = QLabel("SCHOOL ACADEMIC PORTAL")
    kicker.setObjectName("authKicker")
    layout.addWidget(kicker)

    title = QLabel("Grading System")
    title.setObjectName("authBrandTitle")
    layout.addWidget(title)

    copy = QLabel("One place for school records, class grades, and student progress.")
    copy.setObjectName("authBrandCopy")
    copy.setWordWrap(True)
    layout.addWidget(copy)
    layout.addStretch()

    footer = QLabel("Administrator and teacher access, plus student gradebooks")
    footer.setObjectName("authFooter")
    footer.setWordWrap(True)
    layout.addWidget(footer)
    return panel


def _build_auth_card(title_text: str, subtitle_text: str) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("authCard")
    card.setMinimumWidth(390)
    card.setMaximumWidth(500)
    card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(36, 34, 36, 32)
    layout.setSpacing(11)

    title = QLabel(title_text)
    title.setObjectName("authTitle")
    layout.addWidget(title)

    subtitle = QLabel(subtitle_text)
    subtitle.setObjectName("authSubtitle")
    subtitle.setWordWrap(True)
    layout.addWidget(subtitle)
    layout.addSpacing(8)
    return card, layout


def _field(label_text: str, input_widget: QLineEdit) -> QWidget:
    wrapper = QWidget()
    layout = QVBoxLayout(wrapper)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    label = QLabel(label_text)
    label.setObjectName("fieldLabel")
    layout.addWidget(label)
    layout.addWidget(input_widget)
    return wrapper


class LoginWidget(QWidget):
    authenticated = pyqtSignal()
    switch_to_register = pyqtSignal()

    def __init__(self, auth_service: AuthenticationService, student_service: StudentService):
        super().__init__()
        self.auth_service = auth_service
        self.student_service = student_service
        self.setObjectName("authPage")
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        layout.addWidget(_build_brand_panel(), stretch=1)

        card, card_layout = _build_auth_card(
            "Sign in",
            "Choose staff access or open your student gradebook.",
        )
        tabs = QTabWidget()
        tabs.setObjectName("authTabs")

        staff_tab = QWidget()
        staff_layout = QVBoxLayout(staff_tab)
        staff_layout.setContentsMargins(4, 12, 4, 4)
        staff_layout.setSpacing(11)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Staff username")
        self.username_input.setClearButtonEnabled(True)
        staff_layout.addWidget(_field("Administrator or teacher", self.username_input))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        staff_layout.addWidget(_field("Password", self.password_input))

        staff_btn = QPushButton("Sign in to staff workspace")
        staff_btn.setObjectName("primaryButton")
        staff_btn.clicked.connect(self._handle_staff_login)
        staff_layout.addSpacing(5)
        staff_layout.addWidget(staff_btn)
        register_btn = QPushButton("Register as a teacher or student")
        register_btn.setObjectName("linkButton")
        register_btn.clicked.connect(self.switch_to_register.emit)
        staff_layout.addWidget(register_btn)
        staff_layout.addStretch()
        self.password_input.returnPressed.connect(self._handle_staff_login)
        tabs.addTab(staff_tab, "Staff")

        student_tab = QWidget()
        student_layout = QVBoxLayout(student_tab)
        student_layout.setContentsMargins(4, 12, 4, 4)
        student_layout.setSpacing(11)
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Enter your registered Student ID")
        self.student_id_input.setMaxLength(10)
        student_layout.addWidget(_field("Student ID", self.student_id_input))

        student_hint = QLabel("Your Student ID opens your personal, read-only gradebook.")
        student_hint.setObjectName("helperLabel")
        student_hint.setWordWrap(True)
        student_layout.addWidget(student_hint)

        student_btn = QPushButton("Open my gradebook")
        student_btn.setObjectName("primaryButton")
        student_btn.clicked.connect(self._handle_student_login)
        student_layout.addWidget(student_btn)
        student_layout.addStretch()
        self.student_id_input.returnPressed.connect(self._handle_student_login)
        tabs.addTab(student_tab, "Student")

        card_layout.addWidget(tabs)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _handle_staff_login(self):
        try:
            self.auth_service.authenticate(
                self.username_input.text().strip(),
                self.password_input.text(),
            )
            self.username_input.clear()
            self.password_input.clear()
            self.authenticated.emit()
        except (ValueError, TypeError) as err:
            QMessageBox.warning(self, "Sign in failed", str(err))
        except RuntimeError as err:
            QMessageBox.critical(self, "Database error", str(err))

    def _handle_student_login(self):
        try:
            self.auth_service.authenticate_student(
                self.student_id_input.text(),
                self.student_service,
            )
            self.student_id_input.clear()
            self.authenticated.emit()
        except (KeyError, ValueError, TypeError) as err:
            QMessageBox.warning(self, "Student not found", str(err))
        except RuntimeError as err:
            QMessageBox.critical(self, "Database error", str(err))


class RegisterWidget(QWidget):
    registered = pyqtSignal()
    switch_to_login = pyqtSignal()

    def __init__(self, auth_service: AuthenticationService, student_service: StudentService):
        super().__init__()
        self.auth_service = auth_service
        self.student_service = student_service
        self.setObjectName("authPage")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        layout.addWidget(_build_brand_panel(), stretch=1)

        card, card_layout = _build_auth_card(
            "Create an account",
            "Register a teacher account or create a student gradebook.",
        )

        tabs = QTabWidget()
        tabs.setObjectName("authTabs")
        teacher_tab = QWidget()
        teacher_layout = QVBoxLayout(teacher_tab)
        teacher_layout.setContentsMargins(4, 12, 4, 4)
        teacher_layout.setSpacing(9)
        self.teacher_name_input = QLineEdit()
        self.teacher_name_input.setPlaceholderText("Full name")
        teacher_layout.addWidget(_field("Teacher name", self.teacher_name_input))
        self.teacher_username_input = QLineEdit()
        self.teacher_username_input.setPlaceholderText("Create a username")
        teacher_layout.addWidget(_field("Username", self.teacher_username_input))
        self.teacher_password_input = QLineEdit()
        self.teacher_password_input.setPlaceholderText("At least 6 characters")
        self.teacher_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        teacher_layout.addWidget(_field("Password", self.teacher_password_input))
        self.teacher_confirm_input = QLineEdit()
        self.teacher_confirm_input.setPlaceholderText("Repeat the password")
        self.teacher_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        teacher_layout.addWidget(_field("Confirm password", self.teacher_confirm_input))
        teacher_button = QPushButton("Register as teacher")
        teacher_button.setObjectName("primaryButton")
        teacher_button.clicked.connect(self._register_teacher)
        teacher_layout.addWidget(teacher_button)
        teacher_layout.addStretch()
        tabs.addTab(teacher_tab, "Teacher")

        student_tab = QWidget()
        student_layout = QVBoxLayout(student_tab)
        student_layout.setContentsMargins(4, 12, 4, 4)
        student_layout.setSpacing(9)
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("00000-YYYY")
        self.student_id_input.setMaxLength(10)
        student_layout.addWidget(_field("Student ID", self.student_id_input))
        self.student_name_input = QLineEdit()
        self.student_name_input.setPlaceholderText("Full name")
        student_layout.addWidget(_field("Student name", self.student_name_input))
        student_hint = QLabel("Students use their registered Student ID to sign in.")
        student_hint.setObjectName("helperLabel")
        student_hint.setWordWrap(True)
        student_layout.addWidget(student_hint)
        student_button = QPushButton("Register student")
        student_button.setObjectName("primaryButton")
        student_button.clicked.connect(self._register_student)
        student_layout.addWidget(student_button)
        student_layout.addStretch()
        tabs.addTab(student_tab, "Student")
        card_layout.addWidget(tabs)

        back_btn = QPushButton("Back to sign in")
        back_btn.setObjectName("linkButton")
        back_btn.clicked.connect(self.switch_to_login.emit)
        card_layout.addWidget(back_btn)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _register_teacher(self):
        try:
            self.auth_service.register_teacher(
                self.teacher_name_input.text(),
                self.teacher_username_input.text(),
                self.teacher_password_input.text(),
                self.teacher_confirm_input.text(),
            )
            QMessageBox.information(self, "Registration complete", "Teacher account created. You can now sign in.")
            self.teacher_name_input.clear()
            self.teacher_username_input.clear()
            self.teacher_password_input.clear()
            self.teacher_confirm_input.clear()
            self.registered.emit()
        except (ValueError, TypeError) as err:
            QMessageBox.warning(self, "Could not register teacher", str(err))
        except RuntimeError as err:
            QMessageBox.critical(self, "Database error", str(err))

    def _register_student(self):
        try:
            student = self.student_service.add_student(
                self.student_id_input.text(),
                self.student_name_input.text(),
            )
            QMessageBox.information(
                self,
                "Registration complete",
                f"Student account created for {student.name}. Sign in with Student ID {student.student_id}.",
            )
            self.student_id_input.clear()
            self.student_name_input.clear()
            self.registered.emit()
        except (ValueError, TypeError, RuntimeError) as err:
            QMessageBox.warning(self, "Could not register student", str(err))


class AuthView(QStackedWidget):
    user_authenticated = pyqtSignal()

    def __init__(self, auth_service: AuthenticationService, student_service: StudentService):
        super().__init__()
        self.auth_service = auth_service
        self.login_widget = LoginWidget(auth_service, student_service)
        self.register_widget = RegisterWidget(auth_service, student_service)
        self.addWidget(self.login_widget)
        self.addWidget(self.register_widget)

        self.login_widget.authenticated.connect(self.user_authenticated.emit)
        self.login_widget.switch_to_register.connect(lambda: self.setCurrentWidget(self.register_widget))
        self.register_widget.switch_to_login.connect(lambda: self.setCurrentWidget(self.login_widget))
        self.register_widget.registered.connect(lambda: self.setCurrentWidget(self.login_widget))
