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
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from features.Auth.view import AuthView
from features.students.view import StudentsView
from features.grades.view import GradesView
from features.dashboard.teachers import TeacherAccountsView
from features.students.portal import StudentPortal
from features.dashboard.service import UIService
from features.dashboard.model import UserRole


class DashboardWidget(QWidget):
    def __init__(self, ui_service: UIService):
        super().__init__()
        self.ui_service = ui_service
        self.setObjectName("pageSurface")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._init_ui()

    def set_role(self, role: UserRole):
        if role == UserRole.TEACHER:
            self.page_title.setText("Class overview")
            self.page_subtitle.setText("Review student records and school grade activity.")
        else:
            self.page_title.setText("School overview")
            self.page_subtitle.setText("Review all student records, grades, and school performance.")

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
        self.page_title = QLabel("School overview")
        self.page_title.setObjectName("pageTitle")

        self.page_subtitle = QLabel("Review all student records, grades, and school performance.")
        self.page_subtitle.setObjectName("pageSubtitle")

        text_layout.addWidget(eyebrow)
        text_layout.addWidget(self.page_title)
        text_layout.addWidget(self.page_subtitle)

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

        self.card_students = self._create_card("Total Students", "0", "01", "#38BDF8")
        self.card_grades = self._create_card("Grade Records", "0", "02", "#A78BFA")
        self.card_avg = self._create_card("System Average", "0.0%", "03", "#34D399")

        cards_layout.addWidget(self.card_students["frame"], 0, 0)
        cards_layout.addWidget(self.card_grades["frame"], 0, 1)
        cards_layout.addWidget(self.card_avg["frame"], 0, 2)

        layout.addLayout(cards_layout)

        overview = QFrame()
        overview.setObjectName("tableCard")
        overview_layout = QVBoxLayout(overview)
        overview_layout.setContentsMargins(14, 14, 14, 14)
        overview_layout.setSpacing(10)

        overview_header = QHBoxLayout()
        overview_title = QLabel("Student and grade overview")
        overview_title.setObjectName("sectionTitle")
        self.overview_search = QLineEdit()
        self.overview_search.setPlaceholderText("Filter students, IDs, or subjects")
        self.overview_search.setClearButtonEnabled(True)
        self.overview_search.textChanged.connect(self._filter_overview)
        overview_header.addWidget(overview_title)
        overview_header.addStretch()
        overview_header.addWidget(self.overview_search)
        overview_layout.addLayout(overview_header)

        self.overview_table = QTableWidget(0, 4)
        self.overview_table.setHorizontalHeaderLabels(["Student ID", "Student", "Subject", "Score"])
        self.overview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.overview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.overview_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.overview_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.overview_table.verticalHeader().setVisible(False)
        self.overview_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.overview_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.overview_table.setAlternatingRowColors(True)
        self.overview_table.setShowGrid(False)
        self.overview_table.setMinimumHeight(240)
        overview_layout.addWidget(self.overview_table, stretch=1)
        layout.addWidget(overview, stretch=1)

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
        try:
            rows = self.ui_service.get_student_grade_overview()
            self.overview_table.setRowCount(0)
            for record in rows:
                row = self.overview_table.rowCount()
                self.overview_table.insertRow(row)
                values = (
                    record.student_id,
                    record.name,
                    record.subject,
                    f"{record.score:.2f}%" if record.score is not None else "--",
                )
                for column, value in enumerate(values):
                    self.overview_table.setItem(row, column, QTableWidgetItem(value))
            self._filter_overview(self.overview_search.text())
        except RuntimeError as err:
            QMessageBox.warning(self, "Could not load overview", str(err))

    def _filter_overview(self, query: str):
        query = query.strip().casefold()
        for row in range(self.overview_table.rowCount()):
            row_text = " ".join(
                self.overview_table.item(row, column).text()
                for column in range(self.overview_table.columnCount())
                if self.overview_table.item(row, column)
            ).casefold()
            self.overview_table.setRowHidden(row, bool(query) and query not in row_text)


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

        self.auth_view = AuthView(self.auth_service, self.student_service)
        self.auth_view.user_authenticated.connect(self._on_login_success)
        self.root_stack.addWidget(self.auth_view)

        self.workspaces = {}
        for role in (UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT):
            workspace = self._build_workspace_ui(role)
            self.workspaces[role] = workspace
            self.root_stack.addWidget(workspace["widget"])

        self.root_stack.setCurrentIndex(0)

    def _build_workspace_ui(self, role: UserRole) -> dict:
        container = QWidget()
        container.setObjectName(f"{role.value}Workspace")
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
        brand_tagline = QLabel({
            UserRole.ADMIN: "School administration",
            UserRole.TEACHER: "Teaching workspace",
            UserRole.STUDENT: "Student portal",
        }[role])
        brand_tagline.setObjectName("brandTagline")
        brand_layout.addWidget(app_title)
        brand_layout.addWidget(brand_tagline)

        sidebar_layout.addLayout(brand_layout)
        sidebar_layout.addSpacing(26)

        nav_label = QLabel("WORKSPACE")
        nav_label.setObjectName("navSectionLabel")
        sidebar_layout.addWidget(nav_label)
        sidebar_layout.addSpacing(3)

        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        sidebar_layout.addLayout(nav_layout)
        nav_btns = []

        sidebar_layout.addStretch()

        profile_panel = QFrame()
        profile_panel.setObjectName("profilePanel")
        profile_layout = QVBoxLayout(profile_panel)
        profile_layout.setContentsMargins(12, 11, 12, 11)
        profile_layout.setSpacing(3)

        profile_eyebrow = QLabel("SIGNED IN AS")
        profile_eyebrow.setObjectName("profileEyebrow")
        user_name_label = QLabel("Administrator")
        user_name_label.setObjectName("profileName")
        user_role_label = QLabel(f"{role.value.title()} workspace")
        user_role_label.setObjectName("profileRole")
        profile_layout.addWidget(profile_eyebrow)
        profile_layout.addWidget(user_name_label)
        profile_layout.addWidget(user_role_label)
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

        content_stack = QStackedWidget()
        pages = {}
        nav_btns = []
        if role in (UserRole.ADMIN, UserRole.TEACHER):
            dashboard_view = DashboardWidget(self.ui_service)
            dashboard_view.set_role(role)
            students_view = StudentsView(self.student_service)
            grades_view = GradesView(self.grade_service)
            students_view.student_deleted.connect(grades_view.clear_student)
            pages = {"dashboard": dashboard_view, "students": students_view, "grades": grades_view}
            content_stack.addWidget(dashboard_view)
            content_stack.addWidget(students_view)
            content_stack.addWidget(grades_view)
            if role == UserRole.ADMIN:
                grades_view.set_role(UserRole.ADMIN.value)
                teacher_accounts_view = TeacherAccountsView(self.auth_service)
                pages["teachers"] = teacher_accounts_view
                content_stack.addWidget(teacher_accounts_view)
            else:
                students_view.set_teacher_mode()
                grades_view.set_role(UserRole.TEACHER.value)
            destinations = (
                [("Overview", 0), ("Students", 1), ("Grades", 2), ("Teachers", 3)]
                if role == UserRole.ADMIN
                else [("Class overview", 0), ("Students", 1), ("Gradebook", 2)]
            )
        else:
            student_portal = StudentPortal(self.grade_service)
            pages = {"portal": student_portal}
            content_stack.addWidget(student_portal)
            destinations = [("My gradebook", 0)]

        for label, index in destinations:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, page=index, user_role=role: self._switch_tab(user_role, page))
            nav_btns.append((index, btn))
            nav_layout.addWidget(btn)
        nav_layout.addStretch()

        content_layout.addWidget(content_stack)

        main_layout.addWidget(sidebar, stretch=0)
        main_layout.addWidget(content_container, stretch=1)

        return {
            "widget": container,
            "role": role,
            "nav_btns": nav_btns,
            "user_name_label": user_name_label,
            "content_stack": content_stack,
            "pages": pages,
        }

    def _switch_tab(self, role: UserRole, index: int):
        workspace = self.workspaces[role]
        workspace["content_stack"].setCurrentIndex(index)
        for page_index, btn in workspace["nav_btns"]:
            btn.setChecked(page_index == index)

        if role == UserRole.STUDENT:
            current_user = self.auth_service.current_user or {}
            workspace["pages"]["portal"].load_student(current_user)
        elif index == 0:
            dashboard = workspace["pages"].get("dashboard")
            if dashboard:
                dashboard.refresh_stats()
        elif role == UserRole.ADMIN and index == 3:
            workspace["pages"]["teachers"].refresh()

    def _on_login_success(self):
        current_user = self.auth_service.current_user or {}
        try:
            role = UserRole(str(current_user.get("role", UserRole.ADMIN.value)).lower())
        except ValueError:
            QMessageBox.critical(self, "Access denied", "This account has an unsupported role.")
            self.auth_service.logout()
            return
        self.current_role = role
        workspace = self.workspaces[role]
        workspace["user_name_label"].setText(
            current_user.get("display_name", current_user.get("username", role.value.title()))
        )
        self._switch_tab(role, 0)
        self.root_stack.setCurrentWidget(workspace["widget"])

    def _handle_logout(self):
        self.auth_service.logout()
        self.root_stack.setCurrentIndex(0)

