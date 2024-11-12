import sys
import json
import requests
import hashlib
from PySide6.QtCore import QFile, Qt, Signal, QPoint
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QLabel, QPushButton, QMessageBox, QGraphicsDropShadowEffect, QWidget
from PySide6.QtUiTools import QUiLoader
from Custom_Widgets.Widgets import loadJsonStyle
import resource_images  # 이미지 리소스 파일
from main_ui import MainWindow  # main_ui.py에서 MainWindow 임포트

class ClickableLabel(QLabel):
    """클릭 가능한 라벨"""
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()

class RoundedMainWindow(QMainWindow):
    """둥근 모서리와 그라데이션 배경을 가진 메인 윈도우"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def paintEvent(self, event):
        """둥근 모서리 및 그라데이션 배경을 설정"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#636fa4"))
        gradient.setColorAt(1.0, QColor("#e8cbc0"))
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)
        painter.fillPath(path, gradient)

class LoginWindow(RoundedMainWindow):
    """API 연동을 지원하는 로그인 창"""
    login_successful = Signal()
    lambda_url = 'https://ict2140v26.execute-api.ap-northeast-2.amazonaws.com/api/APP-API'
    api_key = 'GsjDo3N7jW5ooPi4EuxJJ2iVm3T3bkQkaT4e6FbQ'

    def __init__(self, app):
        super().__init__()
        self.app = app  # MainApp 인스턴스를 참조
        self._is_dragging = False
        self._old_pos = QPoint()

        self.setup_ui()
        self.setup_shadow_effect()

        # 신호 연결
        self.login_successful.connect(self.show_main_window)

    def setup_ui(self):
        """UI 구성 요소를 로드하고 설정"""
        loader = QUiLoader()
        ui_file = QFile("./ui/login.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        ui_file.close()

        self.setFixedSize(634, 322)
        loadJsonStyle(self, self.ui)

        # UI 요소 연결
        self.email_input = self.findChild(QLineEdit, 'emailInput')
        self.password_input = self.findChild(QLineEdit, 'passwordInput')
        self.login_button = self.findChild(QPushButton, 'loginButton')
        self.close_icon = self.findChild(QLabel, 'closeIcon')

        # 클릭 가능한 닫기 아이콘 설정
        if self.close_icon:
            self.setup_close_icon()
        else:
            print("Error: closeIcon not found")

        # 로그인 버튼 및 Return 키 이벤트 연결
        if self.login_button:
            self.login_button.clicked.connect(self.handle_login)
        else:
            print("Error: loginButton not found")

        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def setup_shadow_effect(self):
        """메인 윈도우에 그림자 효과를 적용"""
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(30)
        shadow_effect.setOffset(10, 10)
        shadow_effect.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow_effect)

    def setup_close_icon(self):
        """클릭 가능한 닫기 아이콘 설정"""
        clickable_icon = ClickableLabel(self)
        clickable_icon.setGeometry(self.close_icon.geometry())
        clickable_icon.setPixmap(self.close_icon.pixmap())
        clickable_icon.clicked.connect(self.close_application)
        self.close_icon = clickable_icon

    def mousePressEvent(self, event):
        """창 드래그를 위한 이벤트 핸들러"""
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._old_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        """드래그 중 창 이동 처리"""
        if self._is_dragging:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        """드래그 중지"""
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()

    def handle_login(self):
        """로그인 버튼 클릭 처리"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "입력 오류", "ID 또는 Password 항목이 비어있습니다.")
            return

        hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.send_user_credentials(email, hashed_pw)

    def send_user_credentials(self, user_id, user_pw):
        """서버로 사용자 인증 정보를 전송"""
        headers = {'Content-Type': 'application/json', 'x-api-key': self.api_key}
        data = {'id': user_id, 'pw': user_pw}

        try:
            response = requests.post(self.lambda_url, headers=headers, json=data)
            if response.status_code == 200:
                self.process_login_response(response.json())
            else:
                QMessageBox.critical(self, "Login", f"Error: {response.status_code}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Login", f"네트워크 오류: {str(e)}")

    def process_login_response(self, response_data):
        """로그인 응답 데이터를 처리"""
        body_data = json.loads(response_data.get('body', '{}'))
        if body_data.get('message') == 'success':
            self.update_user_info(body_data)
            self.login_successful.emit()
            self.close()
        else:
            QMessageBox.critical(self, "Login", "로그인 실패! 잘못된 자격 증명입니다.")

    def update_user_info(self, data):
        """메인 애플리케이션의 사용자 정보 업데이트"""
        self.app.user_email = data.get('email')
        self.app.user_displayname = data.get('displayname')
        self.app.user_title = data.get('title')
        self.app.user_division = data.get('division')
        self.app.user_h_division = data.get('h_division')
        self.app.print_user_info()

    def close_application(self):
        """애플리케이션 종료"""
        self.close()

    def show_main_window(self):
        """로그인 성공 후 메인 윈도우를 표시"""
        self.main_window = MainWindow(self.app)
        self.main_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow(app)
    window.show()
    sys.exit(app.exec())