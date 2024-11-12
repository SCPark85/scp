from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QColor, QPainter, QPainterPath

class DnsMenuDashboardUI(QWidget):
    """DNS 메뉴의 DASHBOARD 화면 UI"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")
        self.setFixedSize(800, 600)  # 원하는 크기로 조정

        # 레이아웃 설정
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 예시 콘텐츠 추가
        title_label = QLabel("DNS DASHBOARD")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)

    def paintEvent(self, event):
        """둥근 모서리와 반투명 배경 설정"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 반투명 흰색 배경
        background_color = QColor(255, 255, 255, 230)  # 230은 약 90% 투명도
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 15, 15)  # 둥근 모서리 반경 15px
        painter.fillPath(path, background_color)