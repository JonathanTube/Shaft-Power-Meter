import ctypes
from ctypes import wintypes
import logging
import os

from anyio import Path

class WindowsSoundPlayer:
    """
    Windows 音频播放器（基于 PlaySound API）
    支持循环播放和即时停止功能
    """
    def __init__(self):
        # 加载 Windows 多媒体库
        self.winmm = ctypes.WinDLL('winmm.dll')
        
        # 定义 PlaySound 函数原型
        self.winmm.PlaySoundW.argtypes = [
            wintypes.LPCWSTR,  # pszSound: 声音文件路径
            wintypes.HMODULE,  # hmod: 模块句柄（通常为 NULL）
            wintypes.DWORD     # fdwSound: 播放标志
        ]
        self.winmm.PlaySoundW.restype = wintypes.BOOL
        
        # 定义播放标志常量
        self.SND_ASYNC = 0x0001  # 异步播放
        self.SND_LOOP = 0x0008   # 循环播放
        self.SND_FILENAME = 0x00020000  # 参数是文件名
        self.SND_NODEFAULT = 0x0002  # 不播放默认声音
    
    def play(self):
        """
        播放音频文件
        :param file_path: 音频文件路径（WAV格式）
        :param loop: 是否循环播放
        """
        try:
            # 设置播放标志
            flags = self.SND_ASYNC | self.SND_FILENAME | self.SND_NODEFAULT | self.SND_LOOP
            
            # 转换路径为Windows API需要的宽字符串
            src = os.path.join(Path(__file__).parent.parent.parent,"assets","TF001.WAV")
            wpath = ctypes.c_wchar_p(src)
            
            # 调用PlaySound API
            success = self.winmm.PlaySoundW(wpath, None, flags)
            if not success:
                logging.error(f"播放失败，错误代码: {ctypes.GetLastError()}")
        except:
            logging.exception('exception occured at WindowsSoundPlayer.play')

    def stop(self):
        """停止当前播放的所有声音"""
        # 传入NULL停止播放
        try:
            self.winmm.PlaySoundW(None, None, 0)
        except:
            logging.exception('exception occured at WindowsSoundPlayer.stop')
