import logging
from logging.handlers import TimedRotatingFileHandler
import os


class Logger:
    def __init__(self, console=False, show_sql=True):
        """
        初始化数据库日志记录器
        :param console: 是否输出到控制台（默认False）
        :param show_sql: 是否输出SQL语句（默认False）
        """
        # 配置日志路径
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'info.log')

        # 创建通用日志格式
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # 文件处理器（始终启用）
        file_handler = TimedRotatingFileHandler(
            filename=log_file,
            when='midnight',
            backupCount=15,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)

        # 获取peewee日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)

        peewee_logger = logging.getLogger('peewee')
        peewee_logger.setLevel(logging.DEBUG)
        peewee_logger.propagate = False  # 禁止日志传播到根记录器
        if show_sql:
            peewee_logger.addHandler(file_handler)

        # 控制台处理器（按需启用）
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            if show_sql:
                peewee_logger.addHandler(console_handler)
