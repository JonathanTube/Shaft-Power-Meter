import flet as ft
import random


class LineChart(ft.Container):
    # data_points contains x and y values, x is time like '00:00', y is float
    def __init__(self, max_y: float, threshold: float, unit: str):
        super().__init__()
        self.max_y = max_y
        self.unit = unit
        self.data_list = []
        self.threshold = threshold
        self.expand = True
        self.padding = ft.padding.all(20)

    def update(self, data_list: list[list[str, float]]):
        self.data_list = data_list
        self.__handle_bottom_axis()
        self.__handle_data_line()
        self.__handle_filled_color()
        self.__handle_threshold_line()
        self.content.update()

    def build(self):
        border = ft.BorderSide(
            width=1,
            color=ft.Colors.with_opacity(0.5, ft.Colors.ON_SURFACE)
        )

        self.content = ft.LineChart(
            border=ft.Border(left=border, bottom=border),
            min_y=0,
            max_y=self.max_y,
            left_axis=self.__get_left_axis(),
            bottom_axis=ft.ChartAxis(labels=[], visible=False),
            data_series=[
                ft.LineChartData(
                    color=ft.Colors.TRANSPARENT,
                    above_line_bgcolor=ft.Colors.TRANSPARENT if len(
                        self.data_list) == 0 else ft.Colors.RED,
                    data_points=[]
                ),
                ft.LineChartData(
                    above_line_bgcolor=ft.Colors.SURFACE,
                    curved=True,
                    stroke_width=1,
                    color=ft.Colors.LIGHT_GREEN,
                    data_points=[]
                ),
                ft.LineChartData(
                    color=ft.Colors.RED,
                    stroke_width=1,
                    data_points=[]
                )
            ]
        )

    def __get_left_axis(self):
        labels = []
        step = self.max_y // 10
        for index in range(0, self.max_y + 1, step):
            label = ft.Text(f"{index}{self.unit}")
            cal = ft.ChartAxisLabel(value=index, label=label)
            labels.append(cal)

        return ft.ChartAxis(labels=labels, labels_size=40)

    def __handle_bottom_axis(self):
        labels = []
        for index, item in enumerate(self.data_list):
            cal = ft.ChartAxisLabel(value=index, label=ft.Text(value=item[0]))
            labels.append(cal)

        self.content.bottom_axis.labels = labels
        self.content.bottom_axis.visible = len(labels) > 0

    def __handle_data_line(self):
        data_points = []
        for index, item in enumerate(self.data_list):
            data_points.append(ft.LineChartDataPoint(index, item[1]))

        self.content.data_series[1].data_points = data_points

    def __handle_threshold_line(self):
        data_points = []
        for index in range(len(self.data_list)):
            data_points.append(ft.LineChartDataPoint(index, self.threshold))

        self.content.data_series[2].data_points = data_points

    def __handle_filled_color(self):
        data_points = []
        for index in range(len(self.data_list)):
            data_points.append(ft.LineChartDataPoint(index, self.threshold))

        self.content.data_series[0].data_points = data_points

        filled_color = ft.Colors.RED
        if len(self.data_list) == 0:
            filled_color = ft.Colors.TRANSPARENT
        self.content.data_series[0].above_line_bgcolor = filled_color


def generate_data_list(max_y: int):
    data_list = []
    for i in range(10):
        data_list.append([f"{i:02d}:00", random.randint(1, max_y - 1)])
    # print(data_list)
    return data_list


async def main(page: ft.Page):
    max_y = 10
    threshold = 8
    line_chart = LineChart(max_y, threshold, "kW")
    page.add(line_chart)

    page.add(ft.FilledButton(text="Update",
                             on_click=lambda e: line_chart.update(generate_data_list(max_y))))


ft.app(main)
