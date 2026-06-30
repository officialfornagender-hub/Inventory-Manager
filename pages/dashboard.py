import flet as ft


# =====================================================
# SHOW DASHBOARD
# =====================================================

def show_dashboard(page: ft.Page):

    page.clean()
    page.title  = "Retail Inventory Manager"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ---------- Get logged-in user ----------

    user     = page.session.get("user") or {}
    username = user.get("Username", "User")
    role     = user.get("Role", "Staff")

    # ---------- Navigation ----------

    def open_inventory(e):
        from pages.inventory import show_inventory
        show_inventory(page)

    def open_product_management(e):
        from pages.product_management import show_product_management
        show_product_management(page)

    def open_reports(e):
        from pages.reports import show_reports
        show_reports(page)

    def open_expiry_alerts(e):
        from pages.search import show_expiry_alerts
        show_expiry_alerts(page)

    def open_users(e):
        from pages.users import show_users
        show_users(page)

    def logout(e):
        page.session.clear()
        from pages.login_page import show_login
        show_login(page)

    # ---------- Menu buttons ----------

    def menu_btn(label, icon, on_click, color=ft.colors.BLUE):
        return ft.FilledButton(
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.colors.WHITE, size=20),
                    ft.Text(label, size=15, color=ft.colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=12,
            ),
            width=380,
            height=52,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=color,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

    # ---------- Layout ----------

    page.add(

        ft.Container(height=20),

        ft.Icon(ft.icons.INVENTORY_2, size=50, color=ft.colors.BLUE),

        ft.Text(
            "Inventory Management",
            size=26,
            weight=ft.FontWeight.BOLD,
        ),

        ft.Text(
            f"Welcome, {username}",
            size=16,
        ),

        ft.Text(
            f"Role : {role}",
            size=13,
            color=ft.colors.GREY,
        ),

        ft.Divider(height=24),

        menu_btn("➕  Add Product",        ft.icons.ADD_BOX,         open_inventory),
        ft.Container(height=8),
        menu_btn("📦  Product Management", ft.icons.MANAGE_SEARCH,   open_product_management),
        ft.Container(height=8),
        menu_btn("📊  Reports",            ft.icons.BAR_CHART,       open_reports,      ft.colors.INDIGO),
        ft.Container(height=8),
        menu_btn("⚠️   Expiry Alerts",      ft.icons.WARNING_AMBER,   open_expiry_alerts, ft.colors.ORANGE),
        ft.Container(height=8),

        # Show Users button only for Admin
        menu_btn("👥  Users",              ft.icons.PEOPLE,          open_users,        ft.colors.TEAL)
        if role == "Admin"
        else ft.Container(),

        ft.Container(height=8) if role == "Admin" else ft.Container(),

        menu_btn("🚪  Logout",             ft.icons.LOGOUT,          logout,            ft.colors.RED_400),

        ft.Container(height=20),
    )

    page.update()
