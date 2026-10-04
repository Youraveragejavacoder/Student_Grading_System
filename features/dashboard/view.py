from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QFrame,
    QGridLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

from features.Auth.view import AuthView
from features.students.view import StudentsView
from features.grades.view import GradesView
from features.dashboard.service import UIService
from features.dashboard.model import UserRole


class DashboardWidget(QWidget):
    def __init__(self, ui_service: UIService):
        super().__init__()
        self.ui_service = ui_service
        self.setObjectName("pageSurface")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        eyebrow = QLabel("OVERVIEW")
        eyebrow.setObjectName("eyebrowLabel")
        title = QLabel("Dashboard Overview")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Real-time system overview and performance metrics")
        subtitle.setObjectName("pageSubtitle")

        text_layout.addWidget(eyebrow)
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        refresh_btn = QPushButton("Refresh metrics")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_stats)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        layout.addLayout(header_layout)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(16)

        self.card_students = self._create_card("Total Students", "0", "🎓", "#38BDF8")
        self.card_grades = self._create_card("Grade Records", "0", "📝", "#A78BFA")
        self.card_avg = self._create_card("System Average", "0.0%", "🌟", "#34D399")

        cards_layout.addWidget(self.card_students["frame"], 0, 0)
        cards_layout.addWidget(self.card_grades["frame"], 0, 1)
        cards_layout.addWidget(self.card_avg["frame"], 0, 2)

        layout.addLayout(cards_layout)

        banner = QFrame()
        banner.setObjectName("welcomeBanner")
        banner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(28, 22, 28, 22)

        banner_text_layout = QVBoxLayout()
        banner_text_layout.setSpacing(5)
        b_title = QLabel("Ready to manage student records?")
        b_title.setObjectName("bannerTitle")

        b_desc = QLabel("Use the sidebar navigation on the left to add or modify student records.")
        b_desc.setObjectName("bannerSubtitle")

        banner_text_layout.addWidget(b_title)
        banner_text_layout.addWidget(b_desc)

        action_btn = QPushButton("Quick Refresh →")
        action_btn.setObjectName("bannerBtn")
        action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        action_btn.clicked.connect(self.refresh_stats)

        banner_layout.addLayout(banner_text_layout)
        banner_layout.addStretch()
        banner_layout.addWidget(action_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(banner)
        layout.addStretch()

    def _create_card(self, title: str, initial_val: str, icon: str, color: str) -> dict:
        frame = QFrame()
        frame.setObjectName("statCard")

        frame.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: #1E293B;
                border-top: 1px solid rgba(255, 255, 255, 0.12);
                border-right: 1px solid rgba(255, 255, 255, 0.05);
                border-bottom: 1px solid rgba(0, 0, 0, 0.3);
                border-left: 5px solid {color};
                border-radius: 16px;
            }}
            QFrame#statCard:hover {{
                background-color: #26334D;
            }}
        """)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        f_layout = QVBoxLayout(frame)
        f_layout.setContentsMargins(22, 20, 22, 20)
        f_layout.setSpacing(10)

        top_layout = QHBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {color}; font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;")

        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")

        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        top_layout.addWidget(lbl_icon)

        lbl_val = QLabel(initial_val)
        lbl_val.setStyleSheet("color: #FFFFFF; font-size: 34px; font-weight: 800; font-family: 'Segoe UI', sans-serif;")

        f_layout.addLayout(top_layout)
        f_layout.addWidget(lbl_val)

        return {"frame": frame, "value_label": lbl_val}

    def refresh_stats(self):
        stats = self.ui_service.get_dashboard_stats()
        self.card_students["value_label"].setText(str(stats.total_students))
        self.card_grades["value_label"].setText(str(stats.total_grades))
        self.card_avg["value_label"].setText(f"{stats.average_score}%")


class GradingSystemUI(QMainWindow):
    def __init__(self, student_service, grade_service, auth_service, ui_service: UIService):
        super().__init__()
        self.student_service = student_service
        self.grade_service = grade_service
        self.auth_service = auth_service
        self.ui_service = ui_service

        self.setWindowTitle("Grading System Portal")
        self.setMinimumSize(950, 650)
        self.resize(1150, 720)

        self.root_stack = QStackedWidget()
        self.root_stack.setObjectName("rootCanvas")
        self.setCentralWidget(self.root_stack)

        self.auth_view = AuthView(self.auth_service)
        self.auth_view.user_authenticated.connect(self._on_login_success)
        self.root_stack.addWidget(self.auth_view)

        self.workspace_widget = self._build_workspace_ui()
        self.root_stack.addWidget(self.workspace_widget)

        self.root_stack.setCurrentIndex(0)

    def _build_workspace_ui(self) -> QWidget:
        container = QWidget()
        container.setObjectName("rootCanvas")
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        sidebar = QFrame()
        sidebar.setFixedWidth(238)
        sidebar.setObjectName("sidebar")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 22, 18, 18)
        sidebar_layout.setSpacing(8)

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(3)
        app_title = QLabel("Grading System")
        app_title.setObjectName("brandName")
        brand_tagline = QLabel("Academic records workspace")
        brand_tagline.setObjectName("brandTagline")
        brand_layout.addWidget(app_title)
        brand_layout.addWidget(brand_tagline)

        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(26)

        nav_label = QLabel("WORKSPACE")
        nav_label.setObjectName("navSectionLabel")
        sidebar_layout.addWidget(nav_label)
        sidebar_layout.addSpacing(3)

        self.nav_btns = []
        btn_dash = self._create_nav_button("Overview", 0)
        btn_stud = self._create_nav_button("Students", 1)
        btn_grad = self._create_nav_button("Grades", 2)

        sidebar_layout.addWidget(btn_dash)
        sidebar_layout.addWidget(btn_stud)
        sidebar_layout.addWidget(btn_grad)

        sidebar_layout.addStretch()

        profile_panel = QFrame()
        profile_panel.setObjectName("profilePanel")
        profile_layout = QVBoxLayout(profile_panel)
        profile_layout.setContentsMargins(12, 11, 12, 11)
        profile_layout.setSpacing(3)

        profile_eyebrow = QLabel("SIGNED IN AS")
        profile_eyebrow.setObjectName("profileEyebrow")
        self.user_name_label = QLabel("Administrator")
        self.user_name_label.setObjectName("profileName")
        self.user_role_label = QLabel("Admin workspace")
        self.user_role_label.setObjectName("profileRole")
        profile_layout.addWidget(profile_eyebrow)
        profile_layout.addWidget(self.user_name_label)
        profile_layout.addWidget(self.user_role_label)
        sidebar_layout.addWidget(profile_panel)
        sidebar_layout.addSpacing(8)

        nav_logout = QPushButton("Sign out")
        nav_logout.setObjectName("dangerButton")
        nav_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        nav_logout.clicked.connect(self._handle_logout)
        sidebar_layout.addWidget(nav_logout)

        content_container = QFrame()
        content_container.setObjectName("cardContainer")

        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(0)

        self.content_stack = QStackedWidget()

        self.dashboard_view = DashboardWidget(self.ui_service)
        self.students_view = StudentsView(self.student_service)
        self.grades_view = GradesView(self.grade_service)
        self.students_view.student_deleted.connect(self.grades_view.clear_student)

        self.content_stack.addWidget(self.dashboard_view)
        self.content_stack.addWidget(self.students_view)
        self.content_stack.addWidget(self.grades_view)

        content_layout.addWidget(self.content_stack)

        main_layout.addWidget(sidebar, stretch=0)
        main_layout.addWidget(content_container, stretch=1)

        self._switch_tab(0)
        return container

    def _create_nav_button(self, label: str, index: int) -> QPushButton:
        btn = QPushButton(label)
        btn.setObjectName("navButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self._switch_tab(index))
        self.nav_btns.append(btn)
        return btn

    def _switch_tab(self, index: int):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_btns):
            btn.setChecked(i == index)

        if index == 0:
            self.dashboard_view.refresh_stats()

    def _on_login_success(self):
        current_user = self.auth_service.current_user or {}
        self.user_name_label.setText(current_user.get("username", "Administrator"))

        try:
            role = UserRole(str(current_user.get("role", UserRole.ADMIN.value)).lower())
        except ValueError:
            role = UserRole.ADMIN
        self.user_role_label.setText(f"{role.value.title()} workspace")
        self.apply_role_permissions(role)

        self.dashboard_view.refresh_stats()
        self.root_stack.setCurrentIndex(1)

    def _handle_logout(self):
        self.auth_service.logout()
        self.root_stack.setCurrentIndex(0)

    def apply_role_permissions(self, role: UserRole):
        perms = self.ui_service.get_permissions_for_role(role)

        if hasattr(self.students_view, "add_btn"):
            self.students_view.add_btn.setEnabled(perms.can_add_student)
            self.students_view.update_btn.setEnabled(perms.can_update_student)
            self.students_view.delete_btn.setEnabled(perms.can_delete_student)

        if hasattr(self.grades_view, "add_btn"):
            self.grades_view.add_btn.setEnabled(perms.can_add_grade)
            self.grades_view.update_btn.setEnabled(perms.can_update_grade)
            self.grades_view.delete_btn.setEnabled(perms.can_delete_grade)
