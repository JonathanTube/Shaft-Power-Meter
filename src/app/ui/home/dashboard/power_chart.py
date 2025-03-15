import random

import flet as ft


class PowerChart:
    def __get_y_axis_labels(self):
        labels = []
        for val in range(6):
            actual_val = val * 10
            labels.append(
                ft.ChartAxisLabel(
                    value=actual_val,
                    label=ft.Text(
                        f"{actual_val}kW",
                        size=14,
                        weight=ft.FontWeight.BOLD
                    )
                )
            )
        self.y_axis_labels = labels

    def __get_x_axis_labels(self):
        labels = []
        for val in range(0, 10):
            labels.append(
                ft.ChartAxisLabel(
                    value=val,
                    label=ft.Container(
                        ft.Text(
                            value=str(val),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.with_opacity(
                                0.5, ft.Colors.ON_SURFACE)
                        ),
                        margin=ft.margin.only(top=10)
                    )
                )
            )
        self.x_axis_labels = labels

    def __get_data_serials(self):
        all_points_1 = []
        for x in range(0, 10):
            y = random.randint(1, 4) * 10
            # print(f'y={y}')
            all_points_1.append(ft.LineChartDataPoint(x, y))

        all_points_2 = []
        for x in range(0, 10):
            y = random.randint(1, 4) * 10
            # print(f'y={y}')
            all_points_2.append(ft.LineChartDataPoint(x, y))

        data_serials = [
            ft.LineChartData(
                data_points=all_points_1,
                stroke_width=8,
                color=ft.Colors.LIGHT_GREEN,
                curved=True,
                stroke_cap_round=True
            ),
            ft.LineChartData(
                data_points=all_points_2,
                stroke_width=8,
                color=ft.Colors.LIGHT_BLUE,
                curved=True,
                stroke_cap_round=True
            )
        ]
        self.data_serials = data_serials

    def create(self):
        self.__get_x_axis_labels()
        self.__get_y_axis_labels()
        self.__get_data_serials()
        return ft.LineChart(
            data_series=self.data_serials,
            border=ft.border.only(
                left=ft.BorderSide(
                    1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)
                ),
                bottom=ft.BorderSide(
                    1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)
                )
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=5, color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE), width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE), width=1
            ),
            left_axis=ft.ChartAxis(
                labels=self.y_axis_labels,
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels=self.x_axis_labels,
                labels_size=32,
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            min_y=0,
            max_y=50,
            min_x=0,
            max_x=9,
            # animate=5000
            # expand=True
        )
