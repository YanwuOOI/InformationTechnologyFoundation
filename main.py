import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui.login_window import LoginWindow

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('library.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    try:
        # 设置日志
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info('启动图书管理系统')

        # 创建应用
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # 使用Fusion风格，提供更现代的外观

        # 创建并显示登录窗口
        login_window = LoginWindow()
        login_window.show()

        # 运行应用
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f'程序运行出错: {str(e)}', exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 