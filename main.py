import sys
from PySide6.QtWidgets import QApplication
from login_ui import LoginWindow  # LoginWindow를 임포트합니다.

class MainApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.user_email = None
        self.user_displayname = None
        self.user_title = None
        self.user_division = None

        self.login_window = LoginWindow(self)  # MainApp 인스턴스를 전달
        self.login_window.show()  # 로그인 창 표시

    def print_user_info(self):
        # 사용자 정보 출력
        print("User Information:")
        print(f"Email: {self.user_email}")
        print(f"Display Name: {self.user_displayname}")
        print(f"Title: {self.user_title}")
        print(f"Division: {self.user_division}")

if __name__ == "__main__":
    app = MainApp(sys.argv)
    sys.exit(app.exec())