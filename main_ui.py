from PySide6.QtCore import Qt, QPoint, Signal, QPropertyAnimation, Property, QEasingCurve
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QColor, QPalette, QPainter, QPainterPath, QMouseEvent, QFont, QLinearGradient, QPixmap
from PySide6.QtSvg import QSvgRenderer
import sys

# Dark Theme 적용 함수
def apply_dark_theme(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(25, 25, 25))  # 윈도우 배경색
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(dark_palette)
    app.setStyle("Fusion")

# 원형 버튼 클래스
class CircularButton(QWidget):
    clicked = Signal()  # 클릭 시 발생할 시그널 정의

    def __init__(self, color, hover_text, parent=None):
        super(CircularButton, self).__init__(parent)
        self.default_color = color
        self.hover_text = hover_text
        self.is_hovered = False  # 개별 hover 상태
        self.setFixedSize(13, 13)  # 아이콘 크기 설정

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(self.default_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())

        if self.is_hovered:
            painter.setPen(Qt.black)
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.hover_text)

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

# HoverableLabel: 밑줄 애니메이션 효과를 주는 클래스
class HoverableLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("color: #E8E9EB; font-size: 12px;")
        self._underline_width = 0  # 밑줄 너비
        self.animation = QPropertyAnimation(self, b"underline_width")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

    def getUnderlineWidth(self):
        return self._underline_width

    def setUnderlineWidth(self, width):
        self._underline_width = width
        self.update()

    underline_width = Property(int, getUnderlineWidth, setUnderlineWidth)

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.fontMetrics().horizontalAdvance(self.text()))  # 텍스트 길이에 맞게 밑줄
        self.animation.start()

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self._underline_width)
        self.animation.setEndValue(0)  # 밑줄을 다시 숨김
        self.animation.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._underline_width > 0:
            painter = QPainter(self)
            pen = painter.pen()
            pen.setColor(QColor("#0080FF"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(0, self.height() - 2, self._underline_width, self.height() - 2)

# 메인 윈도우 클래스
class MainWindow(QMainWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1300, 700)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 사용자 정보 가져오기
        self.user_displayname = app.user_displayname or "Guest"
        self.user_title = app.user_title or "Title Not Set"
        self.user_division = app.user_division or "Division Not Set"
        self.user_h_division = app.user_h_division or "H Division Not Set"
        self.user_email = app.user_email or "Email Not Set"

        self.old_pos = QPoint()
        self.is_maximized = False

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 타이틀 바 설정
        self.setup_title_bar(main_layout)

        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # 왼쪽 메뉴바 설정
        self.setup_menu_bar(central_layout)

        # 메인 콘텐츠 영역
        self.central_content = QLabel()
        central_content_layout = QVBoxLayout()
        central_content_layout.addWidget(self.central_content)
        self.central_content.setAlignment(Qt.AlignCenter)
        self.central_content.setStyleSheet("background-color: transparent;")  # 투명 배경

        # 메인 로고 복구
        main_logo_pixmap = QPixmap("./images/main_logo.png").scaled(
            400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.central_content.setPixmap(main_logo_pixmap)

        central_layout.addLayout(central_content_layout)

        main_layout.addWidget(central_widget)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("border-radius: 10px;")
        self.setCentralWidget(main_widget)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#636fa4"))
        gradient.setColorAt(1.0, QColor("#e8cbc0"))

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        painter.fillPath(path, gradient)

    def setup_menu_bar(self, central_layout):
        self.menu_widget = QWidget()
        self.menu_widget.setFixedWidth(250)
        self.menu_widget.setStyleSheet(
            "background-color: #39496d; border-top-left-radius: 0px; border-bottom-left-radius: 10px;"
        )

        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        self.setup_logo(menu_layout)
        self.setup_menu_items(menu_layout)
        self.setup_user_info(menu_layout)

        central_layout.addWidget(self.menu_widget)

    def setup_title_bar(self, main_layout):
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(35)
        self.title_bar.setStyleSheet(
            "background-color: #D3D3D3; border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;"
        )
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)

        self.setup_window_control(title_layout)

        title_label = QLabel("PNSLAB Workspace")
        title_label.setStyleSheet("font-size: 12px; color: #333333;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label, 18)

        title_layout.addStretch(1)
        main_layout.addWidget(self.title_bar)

    def setup_window_control(self, title_layout):
        window_control_widget = QWidget()
        window_control_layout = QHBoxLayout(window_control_widget)
        window_control_layout.setContentsMargins(10, 0, 0, 0)
        window_control_layout.setSpacing(5)

        self.btn_close = CircularButton("#ff5f57", "X")
        self.btn_close.mousePressEvent = self.on_close_clicked

        self.btn_minimize = CircularButton("#ffbd2e", "-")
        self.btn_minimize.mousePressEvent = self.on_minimize_clicked

        self.btn_maximize = CircularButton("#28c940", "+")
        self.btn_maximize.mousePressEvent = self.on_maximize_clicked

        window_control_layout.addWidget(self.btn_close)
        window_control_layout.addWidget(self.btn_minimize)
        window_control_layout.addWidget(self.btn_maximize)

        title_layout.addWidget(window_control_widget, 1)

    def setup_logo(self, menu_layout):
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 20, 0, 10)

        # 텍스트 로고 설정
        logo_label = QLabel()
        logo_label.setText(
            '<span style="color: #d9d9d9; font-size: 18px;">PNSLAB</span>'
            '<span style="color: white; font-size: 18px; font-weight: bold;">Workspace</span>'
        )
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)

        menu_layout.addWidget(logo_widget, 1)

    def setup_menu_items(self, menu_layout):
        self.menu_area_widget = QWidget()
        self.menu_area_layout = QVBoxLayout(self.menu_area_widget)
        self.menu_area_layout.setContentsMargins(20, 30, 20, 10)
        self.menu_area_layout.setSpacing(5)
        self.menu_area_layout.setAlignment(Qt.AlignTop)

        # HOME 메뉴
        self.add_menu_item("HOME", "./icons/home_icon.svg", is_svg=True, underline=True)

        # DNS 메뉴
        self.add_menu_item("DNS", "./icons/dns_icon.svg", self.toggle_dns_submenu, is_svg=True, arrow=True)
        self.dns_submenu_widget = self.create_dns_submenu()

        # NETWORK 메뉴
        self.add_menu_item("NETWORK", "./icons/network_icon.svg", self.toggle_network_submenu, is_svg=True, arrow=True)
        self.network_submenu_widget = self.create_network_submenu()

        # FIREWALL 메뉴
        self.add_menu_item("FIREWALL", "./icons/firewall_icon.svg", self.toggle_firewall_submenu, is_svg=True, arrow=True)
        self.firewall_submenu_widget = self.create_firewall_submenu()

        # NOTIFICATION 메뉴
        self.add_menu_item("NOTIFICATION", "./icons/notification_icon.svg", is_svg=True, underline=True)

        # SETTINGS 메뉴
        self.add_menu_item("SETTINGS", "./icons/settings_icon.svg", is_svg=True, underline=True)

        menu_layout.addWidget(self.menu_area_widget, 8)

    def create_dns_submenu(self):
        dns_submenu_widget = QWidget()
        dns_submenu_layout = QVBoxLayout(dns_submenu_widget)
        dns_submenu_layout.setContentsMargins(50, 0, 0, 0)
        dns_submenu_layout.setSpacing(10)

        # 하위 메뉴 항목
        submenu_items = ["DASHBOARD", "TASKS", "SCHEDULE", "LOOKUP"]
        for item in submenu_items:
            submenu_label = HoverableLabel(item)
            dns_submenu_layout.addWidget(submenu_label)

        self.menu_area_layout.insertWidget(2, dns_submenu_widget)
        dns_submenu_widget.setVisible(False)
        return dns_submenu_widget

    def create_network_submenu(self):
        network_submenu_widget = QWidget()
        network_submenu_layout = QVBoxLayout(network_submenu_widget)
        network_submenu_layout.setContentsMargins(50, 0, 0, 0)
        network_submenu_layout.setSpacing(10)

        submenu_items = ["TASKS", "MONITORING"]
        for item in submenu_items:
            submenu_label = HoverableLabel(item)
            network_submenu_layout.addWidget(submenu_label)

        self.menu_area_layout.insertWidget(4, network_submenu_widget)
        network_submenu_widget.setVisible(False)
        return network_submenu_widget

    def create_firewall_submenu(self):
        firewall_submenu_widget = QWidget()
        firewall_submenu_layout = QVBoxLayout(firewall_submenu_widget)
        firewall_submenu_layout.setContentsMargins(50, 0, 0, 0)
        firewall_submenu_layout.setSpacing(10)

        submenu_items = ["DASHBOARD", "LOOKUP"]
        for item in submenu_items:
            submenu_label = HoverableLabel(item)
            firewall_submenu_layout.addWidget(submenu_label)

        self.menu_area_layout.insertWidget(6, firewall_submenu_widget)
        firewall_submenu_widget.setVisible(False)
        return firewall_submenu_widget

    def toggle_dns_submenu(self, arrow_label):
        is_visible = self.dns_submenu_widget.isVisible()
        self.dns_submenu_widget.setVisible(not is_visible)
        self.set_arrow_icon(arrow_label, "./icons/arrow-down.svg" if not is_visible else "./icons/arrow-right.svg")
        self.update_menu_item_style(self.dns_menu_label, self.dns_icon_label, arrow_label, not is_visible)

    def toggle_network_submenu(self, arrow_label):
        is_visible = self.network_submenu_widget.isVisible()
        self.network_submenu_widget.setVisible(not is_visible)
        self.set_arrow_icon(arrow_label, "./icons/arrow-down.svg" if not is_visible else "./icons/arrow-right.svg")
        self.update_menu_item_style(self.network_menu_label, self.network_icon_label, arrow_label, not is_visible)

    def toggle_firewall_submenu(self, arrow_label):
        is_visible = self.firewall_submenu_widget.isVisible()
        self.firewall_submenu_widget.setVisible(not is_visible)
        self.set_arrow_icon(arrow_label, "./icons/arrow-down.svg" if not is_visible else "./icons/arrow-right.svg")
        self.update_menu_item_style(self.firewall_menu_label, self.firewall_icon_label, arrow_label, not is_visible)

    def update_menu_item_style(self, text_label, icon_label, arrow_label, highlight):
        """메뉴 항목 스타일 업데이트: 하이라이트 색상 적용"""
        color = "#0080FF" if highlight else "#E8E9EB"
        text_label.setStyleSheet(f"color: {color}; font-size: 12px;")
        self.update_icon_color(icon_label, color)
        self.update_icon_color(arrow_label, color)

    def update_icon_color(self, icon_label, color):
        """아이콘 색상 업데이트"""
        pixmap = icon_label.pixmap()
        if pixmap:
            painter = QPainter(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor(color))
            painter.end()
            icon_label.setPixmap(pixmap)

    def set_arrow_icon(self, label, icon_path):
        svg_renderer = QSvgRenderer(icon_path)
        pixmap = QPixmap(512, 512)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        painter.begin(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), QColor("#E8E9EB"))  # 기본 색상
        painter.end()

        label.setPixmap(pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def setup_user_info(self, menu_layout):
        user_info_widget = QWidget()
        user_info_layout = QVBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 10, 0, 20)

        displayname_title_label = QLabel(f"{self.user_displayname} {self.user_title}")
        displayname_title_label.setStyleSheet("color: #E8E9EB; font-size: 20px; font-weight: bold;")
        displayname_title_label.setAlignment(Qt.AlignCenter)

        division_label = QLabel(f"{self.user_h_division} / {self.user_division}")
        division_label.setStyleSheet("color: #90a4ae; font-size: 12px;")
        division_label.setAlignment(Qt.AlignCenter)

        email_label = QLabel(self.user_email)
        email_label.setStyleSheet("color: #90a4ae; font-size: 12px;")
        email_label.setAlignment(Qt.AlignCenter)

        user_info_layout.addWidget(displayname_title_label)
        user_info_layout.addWidget(division_label)
        user_info_layout.addWidget(email_label)

        menu_layout.addWidget(user_info_widget, 1)

    def add_menu_item(self, text, icon_path=None, callback=None, is_svg=False, arrow=False, underline=False):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 5, 0, 5)
        item_layout.setSpacing(8)

        icon_label = QLabel()

        if is_svg and icon_path.endswith('.svg'):
            svg_renderer = QSvgRenderer(icon_path)
            pixmap_size = 512  # 높은 해상도
            pixmap = QPixmap(pixmap_size, pixmap_size)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()

            painter.begin(pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(pixmap.rect(), QColor("#FFFFFF"))
            painter.end()

            scaled_pixmap = pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            icon_pixmap = QPixmap(icon_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)

        icon_label.setFixedWidth(24)
        item_layout.addWidget(icon_label)

        text_label = HoverableLabel(text) if underline else QLabel(text)
        text_label.setStyleSheet("color: #E8E9EB; font-size: 12px;")
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        item_layout.addWidget(text_label, 1)

        arrow_label = QLabel()
        if arrow:
            self.set_arrow_icon(arrow_label, "./icons/arrow-right.svg")
            arrow_label.setFixedWidth(24)
            item_layout.addWidget(arrow_label)

        # 특정 메뉴에 대해 속성 저장
        if text == "DNS":
            self.dns_menu_label = text_label
            self.dns_icon_label = icon_label
        elif text == "NETWORK":
            self.network_menu_label = text_label
            self.network_icon_label = icon_label
        elif text == "FIREWALL":
            self.firewall_menu_label = text_label
            self.firewall_icon_label = icon_label

        if callback:
            item_widget.mousePressEvent = lambda event: callback(arrow_label)

        self.menu_area_layout.addWidget(item_widget)

    def on_close_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.close()

    def on_minimize_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.showMinimized()

    def on_maximize_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize_restore()

    def toggle_maximize_restore(self):
        if self.is_maximized:
            self.showNormal()
            self.resize(1300, 700)
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

    def mousePressEvent(self, event):
        # 타이틀바 영역에서만 드래그 가능
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.old_pos = event.globalPosition().toPoint()
        else:
            self.old_pos = QPoint()  # 드래그 불가

    def mouseMoveEvent(self, event):
        if not self.old_pos.isNull() and not self.is_maximized:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = QPoint()

if __name__ == "__main__":
    from main import MainApp  # MainApp과 연동
    app = MainApp(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    sys.exit(app.exec())