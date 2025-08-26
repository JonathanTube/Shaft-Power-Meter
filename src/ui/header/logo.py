import logging
import flet as ft
import os
from pathlib import Path


class HeaderLogo(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def get_src(self):
        try:
            # Choose asset by theme
            asset_name = "logo_dark.png" if (self.page is not None and self.page.theme_mode == ft.ThemeMode.LIGHT) else "logo_light.png"

            # Prefer served asset URL when available (works across desktop/web)
            try:
                if self.page is not None and hasattr(self.page, "get_asset_url"):
                    return self.page.get_asset_url(asset_name)
            except Exception:
                pass

            # Fallback to file URI if asset URL is unavailable
            base_dir = Path(__file__).parent.parent.parent / "assets"
            candidate = base_dir / asset_name
            try:
                if candidate.exists():
                    return candidate.as_uri()
            except Exception:
                pass

            # Final fallback: relative assets path (requires assets_dir configured)
            return f"assets/{asset_name}"
        except:
            logging.exception('exception occured at HeaderLogo.get_src')

    def update_style(self):
        try:
            if self.content and self.content.page:
                self.content.src = self.get_src()
                self.content.update()
        except:
            logging.exception('exception occured at HeaderLogo.update_style')

    def before_update(self):
        try:
            self.content = ft.Image(src=self.get_src(), fit=ft.ImageFit.FILL)
        except:
            logging.exception('exception occured at HeaderLogo.before_update')
