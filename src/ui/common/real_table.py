import flet as ft

from abstract_table import AbstractTable


class RealTable(AbstractTable):
    def load_data(self, page: int, page_size: int):
        print(f"Loading data for page {page} and page size {page_size}")
        return [
            ["1", "Report 1", "2021-01-01"],
            ["2", "Report 2", "2021-01-02"],
            ["3", "Report 3", "2021-01-03"],
            ["4", "Report 4", "2021-01-04"],
            ["5", "Report 5", "2021-01-05"],
            ["6", "Report 6", "2021-01-06"],
            ["7", "Report 7", "2021-01-07"],
            ["8", "Report 8", "2021-01-08"],
            ["9", "Report 9", "2021-01-09"],
            ["10", "Report 10", "2021-01-10"],
            ["11", "Report 11", "2021-01-11"],
            ["12", "Report 12", "2021-01-12"],
            ["13", "Report 13", "2021-01-13"],
            ["14", "Report 14", "2021-01-14"],
            ["15", "Report 15", "2021-01-15"],
            ["16", "Report 16", "2021-01-16"],
            ["17", "Report 17", "2021-01-17"],
            ["18", "Report 18", "2021-01-18"],
            ["19", "Report 19", "2021-01-19"],
            ["20", "Report 20", "2021-01-20"]
        ]

    def create_columns(self):
        return ["No.", "Report Name", "Create At"]

    def has_operations(self):
        return True

    def create_operations(self, _id: int):
        return ft.Row([
            ft.IconButton(
                ft.icons.EDIT, on_click=lambda e: self.edit_report(_id)),
            ft.IconButton(ft.icons.DELETE,
                          on_click=lambda e: self.delete_report(_id))
        ])


async def main(page: ft.Page):
    table = RealTable()
    page.add(table)

ft.app(main)
