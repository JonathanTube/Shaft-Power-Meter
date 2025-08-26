import logging
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
import os
import sys
import win32api
import queue
import atexit


class Logger:
    def __init__(self, show_sql=True):
        """
        初始化数据库日志记录器（异步版本，自动退出时安全清空队列）
        :param show_sql: 是否输出SQL语句
        """
        # 配置日志路径
        log_dir = os.path.join(self.get_exe_dir(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'info.log')

        # 通用日志格式
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

        # 日志队列（无限长度）
        self.log_queue = queue.Queue(-1)

        # 文件处理器（按天切割，保留 15 天）
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            backupCount=15,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # 后台日志监听器
        self.listener = QueueListener(self.log_queue, file_handler, console_handler)
        self.listener.start()

        # 根日志器使用队列处理器
        queue_handler = QueueHandler(self.log_queue)
        logging.basicConfig(level=logging.DEBUG, handlers=[queue_handler])

        # SQL 日志（peewee）
        if show_sql:
            peewee_logger = logging.getLogger('peewee')
            peewee_logger.setLevel(logging.DEBUG)
            peewee_logger.propagate = False

            peewee_queue_handler = QueueHandler(self.log_queue)
            peewee_logger.addHandler(peewee_queue_handler)

        # 注册退出钩子
        atexit.register(self.stop)

    def get_exe_dir(self):
        if getattr(sys, 'frozen', False):
            exe_path = win32api.GetLongPathName(sys.executable)
            return os.path.dirname(exe_path)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def stop(self):
        """关闭日志监听器（确保队列日志写完）"""
        try:
            logging.info('关闭日志监听器')
            self.listener.stop()
        except Exception:
            pass
