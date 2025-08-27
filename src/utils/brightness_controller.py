import ctypes
from ctypes import wintypes

# 常量定义
FILE_DEVICE_UNKNOWN = 0x00000022
METHOD_BUFFERED = 0
FILE_WRITE_ACCESS = 0x0002


def CTL_CODE(device_type, function, method, access):
    return (device_type << 16) | (access << 14) | (function << 2) | method


IOCTL_ADVBRIGHTNESS_GET_VALUE = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x9b0, METHOD_BUFFERED, FILE_WRITE_ACCESS)
IOCTL_ADVBRIGHTNESS_SET_VALUE = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x9b1, METHOD_BUFFERED, FILE_WRITE_ACCESS)
DEVICE_NAME = r"\\.\AdvBrightnessDev"


class BrightnessController:
    def __init__(self):
        try:
            self.device_handle = None
            self.min_brightness = 0
            self.max_brightness = 100
            self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            self._setup_api_functions()
        except:
            pass

    def _setup_api_functions(self):
        # 设置CreateFileW函数
        self.CreateFileW = self.kernel32.CreateFileW
        self.CreateFileW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE
        ]
        self.CreateFileW.restype = wintypes.HANDLE

        # 设置CloseHandle函数
        self.CloseHandle = self.kernel32.CloseHandle
        self.CloseHandle.argtypes = [wintypes.HANDLE]
        self.CloseHandle.restype = wintypes.BOOL

        # 设置DeviceIoControl函数
        self.DeviceIoControl = self.kernel32.DeviceIoControl
        self.DeviceIoControl.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            wintypes.LPVOID,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
            wintypes.LPVOID
        ]
        self.DeviceIoControl.restype = wintypes.BOOL

        # 错误检查
        def check_error(result, func, args):
            if not result:
                raise ctypes.WinError(ctypes.get_last_error())
            return args

        self.DeviceIoControl.errcheck = check_error

    def open(self):
        """打开亮度设备"""
        # 尝试打开设备
        self.device_handle = self.CreateFileW(
            DEVICE_NAME,
            0x80000000 | 0x40000000,  # GENERIC_READ | GENERIC_WRITE
            1 | 2,                     # FILE_SHARE_READ | FILE_SHARE_WRITE
            None,
            3,                         # OPEN_EXISTING
            0,
            None
        )

        # 检查是否成功打开设备
        INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
        if self.device_handle == INVALID_HANDLE_VALUE:
            error_code = ctypes.get_last_error()
            if error_code == 2:  # 文件未找到错误
                raise FileNotFoundError("驱动未安装或设备不存在")
            else:
                raise ctypes.WinError(error_code)

        # 获取亮度范围
        self._get_brightness_range()

    def close(self):
        """关闭设备"""
        if self.device_handle:
            self.CloseHandle(self.device_handle)
            self.device_handle = None

    def _get_brightness_range(self):
        """获取亮度范围（内部使用）"""
        results = (wintypes.ULONG * 3)()
        bytes_returned = wintypes.DWORD()

        self.DeviceIoControl(
            self.device_handle,
            IOCTL_ADVBRIGHTNESS_GET_VALUE,
            None, 0,
            results, ctypes.sizeof(results),
            ctypes.byref(bytes_returned),
            None
        )
        self.min_brightness = results[1]
        self.max_brightness = results[2]

    def get_percentage(self):
        """获取当前亮度百分比（0-100）"""
        results = (wintypes.ULONG * 3)()
        bytes_returned = wintypes.DWORD()

        self.DeviceIoControl(
            self.device_handle,
            IOCTL_ADVBRIGHTNESS_GET_VALUE,
            None, 0,
            results, ctypes.sizeof(results),
            ctypes.byref(bytes_returned),
            None
        )

        current = results[0]
        # 计算百分比
        if self.max_brightness - self.min_brightness == 0:
            return 100  # 防止除以零

        percentage = int((current - self.min_brightness) /
                         (self.max_brightness - self.min_brightness) * 100)
        return min(max(percentage, 0), 100)  # 确保在0-100范围内

    def set_percentage(self, percent):
        """设置亮度百分比（0-100）"""
        if not 0 <= percent <= 100:
            raise ValueError("亮度百分比必须在0-100之间")

        # 转换为实际亮度值
        value = int(self.min_brightness +
                    (self.max_brightness - self.min_brightness) * percent / 100)

        bytes_returned = wintypes.DWORD()
        self.DeviceIoControl(
            self.device_handle,
            IOCTL_ADVBRIGHTNESS_SET_VALUE,
            ctypes.byref(wintypes.ULONG(value)),
            ctypes.sizeof(wintypes.ULONG),
            None, 0,
            ctypes.byref(bytes_returned),
            None
        )
        return True

    @staticmethod
    def is_installed():
        """
        检测AdvBrightnessDev驱动是否已安装

        返回值:
            bool: True表示驱动已安装，False表示未安装
        """
        # 定义常量
        GENERIC_READ = 0x80000000
        GENERIC_WRITE = 0x40000000
        FILE_SHARE_READ = 1
        FILE_SHARE_WRITE = 2
        OPEN_EXISTING = 3
        INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

        try:
            # 加载Windows API
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

            # 定义CreateFileW函数
            CreateFileW = kernel32.CreateFileW
            CreateFileW.argtypes = [
                wintypes.LPCWSTR,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.LPVOID,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.HANDLE
            ]
            CreateFileW.restype = wintypes.HANDLE

            # 定义CloseHandle函数
            CloseHandle = kernel32.CloseHandle
            CloseHandle.argtypes = [wintypes.HANDLE]
            CloseHandle.restype = wintypes.BOOL

            # 尝试打开设备
            handle = CreateFileW(
                DEVICE_NAME,
                GENERIC_READ | GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                0,
                None
            )

            # 检查是否成功打开设备
            if handle == INVALID_HANDLE_VALUE:
                error_code = ctypes.get_last_error()
                # 错误代码2表示设备未找到（驱动未安装）
                if error_code == 2:
                    return False
                # 其他错误可能表示权限问题或设备已打开
                return False

            # 成功打开设备，关闭句柄并返回True
            CloseHandle(handle)
            return True

        except Exception:
            return False
