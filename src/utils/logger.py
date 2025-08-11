import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import win32api


class Logger:
    def __init__(self, show_sql=True):
        """
        初始化数据库日志记录器
        :param console: 是否输出到控制台（默认False）
        :param show_sql: 是否输出SQL语句（默认False）
        """
        # 配置日志路径
        log_dir = os.path.join(self.get_exe_dir(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'info.log')

        # 创建通用日志格式
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

       # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # 控制台只显示 INFO 及以上
        console_handler.setFormatter(formatter)

        # 文件处理器（始终启用）
        file_handler = TimedRotatingFileHandler(filename=log_file, when='midnight', backupCount=15, encoding='utf-8')
        file_handler.setFormatter(formatter)

        logging.basicConfig(level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S', handlers=[file_handler, console_handler])

        if show_sql:
            peewee_logger = logging.getLogger('peewee')
            peewee_logger.setLevel(logging.DEBUG)
            peewee_logger.propagate = False
            peewee_logger.addHandler(file_handler)
            peewee_logger.addHandler(console_handler)

    def get_exe_dir(self):
        if getattr(sys, 'frozen', False):
            exe_path = win32api.GetLongPathName(sys.executable)
            return os.path.dirname(exe_path)
        else:
            return os.path.dirname(os.path.abspath(__file__))
