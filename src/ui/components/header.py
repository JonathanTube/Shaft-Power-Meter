from ttkbootstrap.widgets import Label, Frame, Button, Checkbutton
import tkinter as tk


class Header(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill="x", padx=20, pady=10)
        # self.config(bootstyle="info")
        self.create_widgets()

    def create_widgets(self):
        self.create_logo()
        self.create_title()
        self.create_theme_switcher()
        self.create_menus()

    def create_logo(self):
        # Logo
        self.logo_image = tk.PhotoImage(file="img/logo.png")
        self.logo_image = self.logo_image.subsample(2,2)  # Redefine the size by subsampling
        self.logo_label = Label(self, image=self.logo_image)
        self.logo_label.pack(side="left")

    def create_title(self):
        # App Name
        self.app_name_label = Label(self, text="Shaft Power Meter", style=None, font=("TkDefaultFont", 18, "bold"))
        self.app_name_label.pack(side="left",padx=20)

    def create_menus(self):
        # Buttons
        self.home_button = Button(self, text="Home")
        self.home_button.pack(side="right", padx=10)

        self.report_button = Button(self, text="Report")
        self.report_button.pack(side="right", padx=10)

        self.setting_button = Button(self, text="Setting")
        self.setting_button.pack(side="right", padx=10)

    def create_theme_switcher(self):
        # Theme Switcher
        self.switch_var = tk.BooleanVar()
        self.switch_button = Checkbutton(
            self, text="dark",
            variable=self.switch_var,
            bootstyle="success-round-toggle")
        self.switch_button.pack(side="right")
