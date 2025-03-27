from datetime import datetime, timedelta
import math
import matplotlib
import matplotlib.pyplot as plt
import flet as ft

from flet.matplotlib_chart import MatplotlibChart

matplotlib.use("svg")


def main(page: ft.Page):
    page.window.maximized = True
    page.window.size = (1024, 768)

    seconds = 24 * 60 * 60
    # 生成示例数据（时间范围：最近24小时，间隔1秒）
    date_times = [
        datetime(2025, 3, 27, 10, 0, 0) + timedelta(seconds=1 * i) for i in range(seconds)
    ]
    rpm_data = [2000 + 500 * (i % 3) for i in range(seconds)]  # RPM模拟数据
    power_data = [50 + 20 * (i % 4) for i in range(seconds)]    # 功率模拟数据

    screen_width = page.window.width
    screen_height = page.window.height
    aspect_ratio = screen_width / screen_height

    fig, ax1 = plt.subplots(figsize=(aspect_ratio*10, 10))

    ax1.set_xlabel('datetime', color='white', fontsize=20)
    ax1.tick_params(axis='x', labelcolor='white', labelsize=16)

    ax1.xaxis.set_major_locator(
        plt.matplotlib.dates.SecondLocator(interval=math.ceil(seconds / 5))
    )
    ax1.xaxis.set_major_formatter(
        plt.matplotlib.dates.DateFormatter('%y-%m-%d %H:%M')
    )

    ax1.set_ylabel('rpm', color='red', fontsize=20)
    ax1.plot(date_times, rpm_data, color='red')
    ax1.tick_params(axis='y', labelcolor='red', labelsize=16)

    ax2 = ax1.twinx()  # instantiate a second Axes that shares the same x-axis

    # we already handled the x-label with ax1
    ax2.set_ylabel('kW', color='blue', fontsize=20)
    ax2.plot(date_times, power_data, color='blue')
    ax2.tick_params(axis='y', labelcolor='blue', labelsize=16)

    page.expand = True
    # 在Flet中显示图像
    page.add(
        ft.Container(
            padding=0,
            content=MatplotlibChart(
                fig,
                transparent=True,
                expand=True
            ),
            expand=True
        )
    )


ft.app(target=main)
