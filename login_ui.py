import sys
import json
import requests
import hashlib
from PySide6.QtCore import QFile, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QLabel, QPushButton, QMessageBox, QGraphicsDropShadowEffect
from PySide6.QtUiTools import QUiLoader
from Custom_Widgets.Widgets import *
import resource_images  # pyside6-rcc ui/images.qrc -o resource_images.py
from main_ui import MainWindow  # main_ui.py에서 MainWindow를 임포트합니다.

class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()

class LoginWindow(QMainWindow):
    login_successful = Signal()

    lambda_url = 'https://ict2140v26.execute-api.ap-northeast-2.amazonaws.com/api/APP-API'
    api_key = 'GsjDo3N7jW5ooPi4EuxJJ2iVm3T3bkQkaT4e6FbQ'

    def __init__(self, app):
        super().__init__()
        self.app = app  # MainApp 인스턴스를 참조
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.load_ui()
        loadJsonStyle(self, self.ui)

        # 그림자 효과 설정
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(30)
        shadow_effect.setOffset(10, 10)
        shadow_effect.setColor(QColor(0, 0, 0, 180))

        self.setGraphicsEffect(shadow_effect)

        self._is_dragging = False
        self._old_pos = None

        # 로그인 성공 시 시그널 연결
        self.login_successful.connect(self.show_main_window)

    def load_ui(self):
        loader = QUiLoader()
        ui_file = QFile("./ui/login.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        self.setCentralWidget(self.ui)
        ui_file.close()

        self.setFixedSize(634, 322)

        self.email_input = self.findChild(QLineEdit, 'emailInput')
        self.password_input = self.findChild(QLineEdit, 'passwordInput')
        self.login_button = self.findChild(QPushButton, 'loginButton')
        self.close_icon = self.findChild(QLabel, 'closeIcon')

        if self.close_icon:
            self.close_icon = ClickableLabel(self)
            self.close_icon.setGeometry(self.findChild(QLabel, 'closeIcon').geometry())
            self.close_icon.setPixmap(self.findChild(QLabel, 'closeIcon').pixmap())
            self.close_icon.clicked.connect(self.close_application)
        else:
            print("Error: closeIcon not found")

        if self.login_button:
            self.login_button.clicked.connect(self.handle_login)
        else:
            print("Error: loginButton not found")

        # Connect returnPressed signal of QLineEdit to handle_login
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        email = self.email_input.text()
        pw = self.password_input.text()

        if not email or not pw:
            QMessageBox.warning(self, "입력 오류", "ID 또는 Password 항목이 비어있습니다.")
            return

        # 패스워드를 SHA-256으로 암호화
        hashed_pw = hashlib.sha256(pw.encode('utf-8')).hexdigest()
        self.send_user_credentials(email, hashed_pw)

    def send_user_credentials(self, user_id, user_pw):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
        data = {
            'id': user_id,
            'pw': user_pw
        }
        response = requests.post(self.lambda_url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = json.loads(response.text)
            body_data = json.loads(response_data['body'])
            if body_data['message'] == 'success':
                # 로그인 성공 시 MainApp 인스턴스에 사용자 정보 업데이트
                self.app.user_email = body_data.get('email')
                self.app.user_displayname = body_data.get('displayname')
                self.app.user_title = body_data.get('title')
                self.app.user_division = body_data.get('division')

                # 사용자 정보 출력
                self.app.print_user_info()

                self.login_successful.emit()  # 로그인 성공 시 시그널 발생
                self.close()  # 로그인 창 닫기
            else:
                QMessageBox.critical(self, "Login", "Login failed! Invalid credentials.")
        else:
            QMessageBox.critical(self, "Login", f"Error: {response.status_code}")

    def close_application(self):
        self.close()

    def show_main_window(self):
        """Login success signal handler to show main window."""
        self.main_window = MainWindow()  # MainWindow 인스턴스 생성
        self.main_window.show()  # 메인 윈도우 표시

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())