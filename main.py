import os
import flet as ft

from database import update_all_status
from pages.login_page import show_login


def main(page: ft.Page):
    # Window Settings
    page.title = "Retail Inventory Manager"
    page.theme_mode = ft.ThemeMode.LIGHT

    # These work only on desktop, so avoid them on web
    if page.web is False:
        page.window.width = 450
        page.window.height = 850

    # Update Product Status
    update_all_status()

    # Open Login Page
    show_login(page)


ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
)