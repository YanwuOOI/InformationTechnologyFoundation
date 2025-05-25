"""
图书管理系统的主入口模块

本模块负责：
1. 配置并初始化日志系统
2. 创建并启动PyQt应用程序
3. 显示登录窗口
4. 处理全局异常
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui.login_window import LoginWindow

def setup_logging():
    """
    配置日志系统
    
    设置:
    - 日志级别：INFO
    - 输出格式：时间 - 模块名 - 日志级别 - 消息
    - 输出目标：文件(library.log)和控制台
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('library.log', encoding='utf-8'),  # 将日志写入文件
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )

def main():
    """
    程序主函数
    
    职责：
    1. 初始化日志系统
    2. 创建Qt应用实例
    3. 设置应用程序样式
    4. 显示登录窗口
    5. 进入事件循环
    """
    try:
        # 初始化日志系统
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