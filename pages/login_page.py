import flet as ft
from auth import login


# =====================================================
# SHOW LOGIN PAGE
# =====================================================

def show_login(page: ft.Page):

    page.clean()
    page.title  = "Retail Inventory Manager"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ---------- Controls ----------

    username_field = ft.TextField(
        label="Username",
        width=320,
        prefix_icon=ft.icons.PERSON,
    )

    password_field = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        width=320,
        prefix_icon=ft.icons.LOCK,
    )

    error_text = ft.Text(
        "",
        color=ft.colors.RED,
        size=13,
        visible=False,
    )

    loading = ft.ProgressRing(visible=False, width=20, height=20)

    # ---------- Events ----------

    def login_clicked(e):

        username = username_field.value.strip()
        password = password_field.value.strip()

        # Validation
        if not username:
            show_error("Please enter Username")
            return

        if not password:
            show_error("Please enter Password")
            return

        # Show loading
        error_text.visible = False
        loading.visible    = True
        login_btn.disabled = True
        page.update()

        # Authenticate
        user = login(username, password)

        loading.visible    = False
        login_btn.disabled = False

        if user:
            page.session.set("user", user)
            from pages.dashboard import show_dashboard
            show_dashboard(page)
        else:
            show_error("Invalid username or password")

        page.update()

    def show_error(message):
        error_text.value   = message
        error_text.visible = True
        page.update()

    def on_enter(e):
        login_clicked(e)

    username_field.on_submit = on_enter
    password_field.on_submit = on_enter

    login_btn = ft.FilledButton(
        "LOGIN",
        width=320,
        height=48,
        on_click=login_clicked,
    )

    # ---------- Layout ----------

    page.add(
        ft.Container(height=60),

        ft.Icon(
            ft.icons.INVENTORY_2,
            size=64,
            color=ft.colors.BLUE,
        ),

        ft.Text(
            "Retail Inventory Manager",
            size=26,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        ),

        ft.Text(
            "Sign in to continue",
            size=14,
            color=ft.colors.GREY,
        ),

        ft.Container(height=30),

        username_field,
        password_field,

        error_text,

        ft.Container(height=10),

        ft.Row(
            [loading, login_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        ),
    )

    page.update()
