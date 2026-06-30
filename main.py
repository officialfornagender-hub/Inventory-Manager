import flet as ft

from database import update_all_status
from pages.login_page import show_login


def main(page: ft.Page):

    # Window Settings
    page.title = "Retail Inventory Manager"
    page.window.width = 450
    page.window.height = 850
    page.theme_mode = ft.ThemeMode.LIGHT

    # Update Product Status in Google Sheet
    update_all_status()

    # Open Login Page
    show_login(page)


ft.app(target=main)
