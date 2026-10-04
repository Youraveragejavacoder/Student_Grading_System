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
    QMessageBox,
    QSizePolicy,
)
from features.Auth.service import AuthenticationService


def _build_brand_panel() -> QFrame:
    panel = QFrame()
    panel.setObjectName("authBrandPanel")
    panel.setMinimumWidth(330)
    panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(42, 42, 42, 42)
    layout.setSpacing(10)

    kicker = QLabel("ACADEMIC WORKSPACE")
    kicker.setObjectName("authKicker")
    layout.addWidget(kicker)

    title = QLabel("Grading System")
    title.setObjectName("authBrandTitle")
    layout.addWidget(title)

    copy = QLabel("A calmer way to manage student records, grades, and everyday academic work.")
    copy.setObjectName("authBrandCopy")
    copy.setWordWrap(True)
    layout.addWidget(copy)

    layout.addSpacing(26)

    for feature in (
        "●  Keep student records organized",
        "●  Review grades at a glance",
        "●  Work from one focused workspace",
    ):
        feature_label = QLabel(feature)
        feature_label.setObjectName("authFeature")
        layout.addWidget(feature_label)

    layout.addStretch()

    footer = QLabel("Simple tools for better academic records")
    footer.setObjectName("authFooter")
    layout.addWidget(footer)
    return panel


def _build_auth_card(title_text: str, subtitle_text: str) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("authCard")
    card.setMinimumWidth(390)
    card.setMaximumWidth(460)
    card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(42, 40, 42, 38)
    layout.setSpacing(11)

    title = QLabel(title_text)
    title.setObjectName("authTitle")
    layout.addWidget(title)

    subtitle = QLabel(subtitle_text)
    subtitle.setObjectName("authSubtitle")
    subtitle.setWordWrap(True)
    layout.addWidget(subtitle)
    layout.addSpacing(13)

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

    def __init__(self, auth_service: AuthenticationService):
        super().__init__()
        self.auth_service = auth_service
        self.setObjectName("authPage")
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        layout.addWidget(_build_brand_panel(), stretch=1)

        card, form_layout = _build_auth_card(
            "Welcome back",
            "Sign in to continue managing your academic records.",
        )

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setClearButtonEnabled(True)
        form_layout.addWidget(_field("Username", self.username_input))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(_field("Password", self.password_input))

        login_btn = QPushButton("Sign in")
        login_btn.setObjectName("primaryButton")
        login_btn.setDefault(True)
        login_btn.clicked.connect(self._handle_login)
        form_layout.addSpacing(7)
        form_layout.addWidget(login_btn)

        reg_btn = QPushButton("New here? Create an account")
        reg_btn.setObjectName("linkButton")
        reg_btn.clicked.connect(self.switch_to_register.emit)
        form_layout.addWidget(reg_btn)

        form_layout.addStretch()

        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.password_input.returnPressed.connect(self._handle_login)

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        try:
            self.auth_service.authenticate(username, password)
            self.username_input.clear()
            self.password_input.clear()
            self.authenticated.emit()
        except ValueError as err:
            QMessageBox.warning(self, "Login Error", str(err))
        except RuntimeError as err:
            QMessageBox.critical(self, "Database Error", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {err}")


class RegisterWidget(QWidget):
    registered = pyqtSignal()
    switch_to_login = pyqtSignal()

    def __init__(self, auth_service: AuthenticationService):
        super().__init__()
        self.auth_service = auth_service
        self.setObjectName("authPage")
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        layout.addWidget(_build_brand_panel(), stretch=1)

        card, form_layout = _build_auth_card(
            "Create your account",
            "Set up a staff account to access the Grading System workspace.",
        )

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        self.username_input.setClearButtonEnabled(True)
        form_layout.addWidget(_field("Username", self.username_input))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(_field("Password", self.password_input))

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Repeat your password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(_field("Confirm password", self.confirm_input))

        helper = QLabel("Use at least 6 characters.")
        helper.setObjectName("helperLabel")
        form_layout.addWidget(helper)

        register_btn = QPushButton("Create account")
        register_btn.setObjectName("primaryButton")
        register_btn.clicked.connect(self._handle_register)
        form_layout.addSpacing(5)
        form_layout.addWidget(register_btn)

        back_btn = QPushButton("Already have an account? Sign in")
        back_btn.setObjectName("linkButton")
        back_btn.clicked.connect(self.switch_to_login.emit)
        form_layout.addWidget(back_btn)

        form_layout.addStretch()
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.confirm_input.returnPressed.connect(self._handle_register)

    def _handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        try:
            self.auth_service.register(username, password, confirm)
            QMessageBox.information(self, "Success", "Account created successfully! You can now log in.")
            self.username_input.clear()
            self.password_input.clear()
            self.confirm_input.clear()
            self.registered.emit()
        except ValueError as err:
            QMessageBox.warning(self, "Registration Error", str(err))
        except RuntimeError as err:
            QMessageBox.critical(self, "Database Error", str(err))
        except Exception as err:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {err}")


class AuthView(QStackedWidget):
    user_authenticated = pyqtSignal()

    def __init__(self, auth_service: AuthenticationService):
        super().__init__()
        self.login_widget = LoginWidget(auth_service)
        self.register_widget = RegisterWidget(auth_service)

        self.addWidget(self.login_widget)
        self.addWidget(self.register_widget)

        self.login_widget.switch_to_register.connect(lambda: self.setCurrentWidget(self.register_widget))
        self.register_widget.switch_to_login.connect(lambda: self.setCurrentWidget(self.login_widget))
        self.login_widget.authenticated.connect(self.user_authenticated.emit)
        self.register_widget.registered.connect(lambda: self.setCurrentWidget(self.login_widget))
