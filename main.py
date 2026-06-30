import os
import flet as ft

from database import update_all_status
from pages.login_page import show_login


def main(page: ft.Page):
    # Page Settings
    page.title = "Retail Inventory Manager"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Desktop window size only
    if not page.web:
        page.window.width = 450
        page.window.height = 850

    # Update Product Status in Google Sheet
    update_all_status()

    # Open Login Page
    show_login(page)


ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,
    port=int(os.environ.get("PORT", 8080)),
)