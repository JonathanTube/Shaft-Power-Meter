from abc import abstractmethod
from typing import final
import flet as ft
from ui.common.pagination import Pagination


@final
class AbstractTable(ft.Card):
    def __init__(self, page_size: int):
        super().__init__()
        self.current_page = 1
        self.page_size = page_size

        self.kwargs = {}  # 其他传入的参数

        self.pg = Pagination(self.page_size, self.__on_page_change)

        self.content = self.__create()
        self.expand = True

    def __on_page_change(self, current_page: int, page_size: int):
        self.current_page = current_page
        self.page_size = page_size
        self.__create_table_rows()

    def __create(self):
        self.__create_table()

        col = ft.Column(
            controls=[self.data_table, self.pg],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER)

        return ft.Container(
            content=col,
            expand=True,
            padding=10
        )

    def __create_table(self):
        columns = self.create_columns()
        if self.has_operations():
            columns.append("Operations")

        wrapped_columns = [ft.DataColumn(ft.Text(column))
                           for column in columns]

        b_size = 0.5
        b_color = ft.colors.INVERSE_SURFACE

        self.data_table = ft.DataTable(
            expand=True,
            heading_row_height=50,
            border_radius=10,
            border=ft.border.all(b_size, b_color),
            vertical_lines=ft.BorderSide(b_size, b_color),
            horizontal_lines=ft.BorderSide(b_size, b_color),
            width=4096,
            columns=wrapped_columns,
            rows=[])

    def __create_cells(self, items):
        cells = []
        for item in items:
            cells.append(ft.DataCell(ft.Text(item)))
        if self.has_operations():
            cells.append(ft.DataCell(self.create_operations(items[0])))

        return cells

    def __create_table_rows(self):
        data = self.load_data()
        rows = []
        for items in data:
            rows.append(ft.DataRow(cells=self.__create_cells(items)))
        self.data_table.rows = rows
        self.data_table.update()

    def did_mount(self):
        self.__create_table_rows()
        total = self.load_total()
        self.pg.update_pagination(total)

    def search(self, **kwargs):
        self.kwargs = kwargs
        self.__create_table_rows()
        total = self.load_total()
        self.pg.update_pagination(total)

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def load_total(self):
        return 0

    @abstractmethod
    def create_columns(self):
        pass

    @abstractmethod
    def has_operations(self):
        return False

    @abstractmethod
    def create_operations(self, _id: int):
        pass
