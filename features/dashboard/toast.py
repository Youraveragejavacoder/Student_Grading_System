from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


def show_side_toast(owner, title: str, message: str) -> None:
    window = owner.window()
    toast = QFrame(window)
    toast.setObjectName("sideToast")
    toast.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    toast.setFixedSize(350, 76)

    layout = QHBoxLayout(toast)
    layout.setContentsMargins(15, 11, 15, 11)
    layout.setSpacing(12)

    icon = QLabel("✓")
    icon.setObjectName("toastIcon")
    icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(icon)

    text_layout = QVBoxLayout()
    text_layout.setContentsMargins(0, 0, 0, 0)
    text_layout.setSpacing(3)

    title_label = QLabel(title)
    title_label.setObjectName("toastTitle")
    message_label = QLabel(message)
    message_label.setObjectName("toastMessage")
    message_label.setWordWrap(True)
    text_layout.addWidget(title_label)
    text_layout.addWidget(message_label)
    layout.addLayout(text_layout, stretch=1)

    toast.move(max(16, window.width() - toast.width() - 22), 22)
    toast.raise_()
    toast.show()

    timer = QTimer(toast)
    timer.setSingleShot(True)
    timer.timeout.connect(toast.deleteLater)
    timer.start(3200)
