from PySide6.QtCore import Qt, QPoint, Signal, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QColor, QPalette, QPainter, QPainterPath, QMouseEvent, QFont, QLinearGradient, QPixmap
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
        # 원형을 그리는 함수
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 부드럽게 처리
        painter.setBrush(QColor(self.default_color))  # 기본 색상 설정
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.width(), self.height())

        # 버튼이 hover 상태일 때 텍스트 표시
        if self.is_hovered:
            painter.setPen(Qt.black)
            font = QFont()
            font.setBold(True)
            font.setPointSize(12)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.hover_text)

    def enterEvent(self, event):
        # 마우스가 버튼에 들어올 때 hover 상태로 변경
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        # 마우스가 버튼에서 나갈 때 hover 상태 해제
        self.is_hovered = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        # 버튼이 클릭될 때 시그널 emit
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

# 메인 윈도우 클래스
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # 기본 프레임 제거
        self.resize(1300, 700)  # 기본 창 크기를 1000x600으로 설정
        self.setAttribute(Qt.WA_TranslucentBackground)  # 창을 반투명 배경으로 설정

        # 드래그 이동을 위한 변수 초기화
        self.old_pos = QPoint()
        self.is_maximized = False  # 최대화 상태를 추적

        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # 모든 여백을 0으로 설정
        main_layout.setSpacing(0)

        # 타이틀 바 설정 (아래쪽 모서리는 직각)
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(35)
        self.title_bar.setStyleSheet(
            "background-color: #D3D3D3; border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;"
        )
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)

        # 아이콘 버튼들 설정
        self.btn_close = CircularButton("#ff5f57", "X")
        self.btn_close.mousePressEvent = self.on_close_clicked

        self.btn_minimize = CircularButton("#ffbd2e", "-")
        self.btn_minimize.mousePressEvent = self.on_minimize_clicked

        self.btn_maximize = CircularButton("#28c940", "+")
        self.btn_maximize.mousePressEvent = self.on_maximize_clicked

        # 아이콘 레이아웃 설정
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.btn_close)
        icon_layout.addWidget(self.btn_minimize)
        icon_layout.addWidget(self.btn_maximize)

        # 타이틀 바에 아이콘 레이아웃 추가
        title_layout.addLayout(icon_layout)
        title_layout.addStretch()
        main_layout.addWidget(self.title_bar)

        # 중앙 레이아웃
        central_widget = QWidget()
        central_layout = QHBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # 왼쪽 메뉴 위젯 설정 (고정 너비 250px, 상단 모서리는 직각, 하단 모서리는 둥글게)
        self.menu_widget = QWidget()
        self.menu_widget.setFixedWidth(250)
        self.menu_widget.setStyleSheet(
            "background-color: #39496d; border-top-left-radius: 0px; border-top-right-radius: 0px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;"
        )
        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setContentsMargins(0, 20, 0, 20)

        # 상단 중앙에 로고 이미지 추가
        logo_label = QLabel()
        logo_pixmap = QPixmap("./images/logo_for_menu.png")
        logo_pixmap = logo_pixmap.scaled(120, logo_pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 너비 200에 맞춰 크기 조정
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)  # 중앙 정렬
        menu_layout.addWidget(logo_label)
        menu_layout.addStretch()

        # 메뉴와 중앙 컨텐츠 추가
        central_layout.addWidget(self.menu_widget)

        # 중앙 컨텐츠 설정 (임의로 텍스트 중앙 배치)
        central_content = QLabel("Main Content Area")
        central_content.setAlignment(Qt.AlignCenter)
        central_content.setStyleSheet("font-size: 18px; color: white;")
        central_layout.addWidget(central_content)
        main_layout.addWidget(central_widget)

        # 메인 위젯 설정
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("border-radius: 10px;")
        self.setCentralWidget(main_widget)

        # 타이틀 바 드래그 및 더블 클릭 이벤트 연결
        self.title_bar.mousePressEvent = self.title_bar_mouse_press_event
        self.title_bar.mouseMoveEvent = self.mouse_move_event
        self.title_bar.mouseDoubleClickEvent = self.title_bar_double_click_event

    # paintEvent를 이용해 둥근 모서리와 그라데이션 적용
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#636fa4"))
        gradient.setColorAt(1.0, QColor("#e8cbc0"))

        # 전체 창에 둥근 모서리 및 그라데이션 적용
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        painter.fillPath(path, gradient)

    # 닫기 버튼 클릭 핸들러
    def on_close_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.close()

    # 최소화 버튼 클릭 핸들러
    def on_minimize_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.showMinimized()

    # 최대화 버튼 클릭 핸들러
    def on_maximize_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize_restore()

    # 최대화/복원 기능
    def toggle_maximize_restore(self):
        if self.is_maximized:
            self.showNormal()
            self.resize(1000, 600)
            self.is_maximized = False
        else:
            self.showMaximized()
            self.is_maximized = True

    # 타이틀 바 드래그 기능
    def title_bar_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouse_move_event(self, event):
        if not self.old_pos.isNull() and not self.is_maximized:
            # 윈도우 이동
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    # 타이틀 바 더블 클릭 시 최대화/복원 기능
    def title_bar_double_click_event(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize_restore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())