import flet as ft
class RS485Output(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page

    def build(self):
        return ft.Text("RS485 Output")
