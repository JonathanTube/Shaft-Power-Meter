from abc import abstractmethod
import logging
import flet as ft
from ui.common.pagination import Pagination


class AbstractTable(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.margin = 0
        self.current_page = 1
        self.page_size = 10
        self.table_width = None
        self.show_checkbox_column = False
        self.kwargs = {}  # 其他传入的参数

    def build(self):
        try:
            # self.default_width = self.page.window.width - \
            #     35 if self.table_width is None else self.table_width
            self.__create_table()

            col = ft.Column(
                controls=[self.data_table],
                expand=True,
                scroll=ft.ScrollMode.ADAPTIVE
            )

            row = ft.Row(
                controls=[col],
                scroll=ft.ScrollMode.ADAPTIVE,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True
            )

            total = self.load_total()
            self.pg = Pagination(total, self.page_size, self.__on_page_change)

            self.content = ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    row,
                    self.pg
                ]
            )
        except:
            logging.exception('exception occured at AbstractTable.build')

    def __on_page_change(self, current_page: int, page_size: int):
        try:
            self.current_page = current_page
            self.page_size = page_size
            total = self.load_total()
            self.pg.update_total(total=total)
            self.__create_table_rows()
        except:
            logging.exception('exception occured at AbstractTable.__on_page_change')

    def __create_table(self):
        self.data_table = ft.DataTable(
            show_checkbox_column=self.show_checkbox_column,
            width=self.table_width,
            expand=True,
            heading_row_height=40,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            data_row_min_height=30,
            # vertical_lines=ft.BorderSide(0.5, ft.Colors.INVERSE_SURFACE),
            # horizontal_lines=ft.BorderSide(0.5, ft.Colors.INVERSE_SURFACE),
            columns=[ft.DataColumn(ft.Text("No Data"))],
            rows=[])

    def __create_cells(self, items: list):
        cells = []
        for item in items:
            cells.append(ft.DataCell(ft.Text(item), data=item, on_double_tap=lambda e: self.__on_double_tap(e, item)))
        if self.has_operations():
            cells.append(ft.DataCell(self.create_operations(items), data=items))

        return cells

    def __on_double_tap(self, e, content):
        self.page.set_clipboard(str(content))

    def __create_table_columns(self):
        if self.page and self.page.session:
            columns = self.create_columns()
            if self.has_operations():
                session = self.page.session
                columns.append(session.get("lang.common.operation"))

            wrapped_columns = [ft.DataColumn(ft.Text(column))for column in columns]
            self.data_table.columns = wrapped_columns

    def __create_table_rows(self):
        try:
            data = self.load_data()
            rows = []
            for items in data:
                rows.append(
                    ft.DataRow(
                        cells=self.__create_cells(items),
                        selected=False,
                        on_select_changed=lambda e: self.__on_select_changed(e)
                    )
                )
            if self.data_table and self.data_table.page:
                self.data_table.rows = rows
                self.data_table.update()
        except:
            logging.exception('exception occured at abstract_table.__create_table_rows')

    def __on_select_changed(self, e):
        if e.control is not None:
            e.control.selected = not e.control.selected
            e.control.update()

    def did_mount(self):
        if self.page is None:
            logging.error('abstract table has not been added to page.')
            return

        try:
            self.__create_table_columns()
            self.__create_table_rows()

            if self.data_table and self.data_table.page:
                self.data_table.update()
        except:
            logging.exception('data_table has not been added to page')

    def search(self, **kwargs):
        try:
            self.kwargs = kwargs
            self.current_page = 1
            self.__create_table_rows()
            if self.pg and self.pg.page:
                self.pg.go_first_page()

                total = self.load_total()
                self.pg.update_total(total)
                self.pg.update()
        except:
            logging.exception('exception occured at abstract_table.search')

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
    def create_operations(self, items: list):
        pass

    def update_columns(self, columns: list[str]):
        if self.page and self.page.session:
            wrapped_columns = [ft.DataColumn(ft.Text(column)) for column in columns]
            if self.has_operations():
                session = self.page.session
                wrapped_columns.append(ft.DataColumn(ft.Text(session.get("lang.common.operation"))))

            self.data_table.columns = wrapped_columns