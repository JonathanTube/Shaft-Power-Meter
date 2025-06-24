import os
import sys
import winshell
import logging

def add_to_startup():
    try:
        # 获取启动文件夹路径
        startup_folder = winshell.startup()
        logging.info(f'startup_folder={startup_folder}')
        # 创建快捷方式
        exe_path = sys.executable
        shortcut_path = os.path.join(startup_folder, "Shaft Power Meter.lnk")

        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = exe_path
            shortcut.description = "Shaft Power Meter"

        return True
    except:
        logging.exception("add to startup error")
        return False
