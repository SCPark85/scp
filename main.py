import sys
from PySide6.QtWidgets import QApplication
from login_ui import LoginWindow  # LoginWindow를 임포트

class MainApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        
        # 사용자 정보 초기화
        self.user_email = None
        self.user_displayname = None
        self.user_title = None
        self.user_division = None

        # 로그인 창 초기화 및 표시
        self.login_window = LoginWindow(self)  
        self.login_window.show()

    def print_user_info(self):
        """사용자 정보를 콘솔에 출력합니다."""
        print("User Information:")
        print(f"Email: {self.user_email}")
        print(f"Display Name: {self.user_displayname}")
        print(f"Title: {self.user_title}")
        print(f"Division: {self.user_division}")

if __name__ == "__main__":
    app = MainApp(sys.argv)
    sys.exit(app.exec())