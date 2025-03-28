import flet as ft
import screen_brightness_control as sbc

def main(page: ft.Page):
    def slider_changed(e):
        sbc.set_brightness(e.control.value)
        # page.update()
    
    slider = ft.Slider(min=0, max=100, on_change=slider_changed)
    page.add(slider)

ft.app(target=main)
