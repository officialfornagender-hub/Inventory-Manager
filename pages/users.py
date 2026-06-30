import flet as ft
from database import get_all_users, add_user, update_user_status

FIELD_WIDTH = 340


# =====================================================
# SHOW USERS (Admin Only)
# =====================================================

def show_users(page: ft.Page):

    page.clean()
    page.title  = "User Management"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    user     = page.session.get("user") or {}
    username = user.get("Username", "Unknown")
    role     = user.get("Role", "Staff")

    # Guard: only Admin
    if role != "Admin":
        page.add(ft.Text("⛔ Access Denied. Admins only.", color=ft.colors.RED, size=18))
        page.update()
        return

    def go_back(e):
        from pages.dashboard import show_dashboard
        show_dashboard(page)

    def snack(msg):
        page.snack_bar      = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    # ---------- Add User Form ----------

    new_username = ft.TextField(label="New Username", width=FIELD_WIDTH)
    new_password = ft.TextField(label="Password", password=True,
                                can_reveal_password=True, width=FIELD_WIDTH)
    new_role = ft.Dropdown(
        label="Role",
        width=FIELD_WIDTH,
        value="Staff",
        options=[
            ft.dropdown.Option("Admin"),
            ft.dropdown.Option("Staff"),
        ],
    )

    def add_user_clicked(e):
        u = new_username.value.strip()
        p = new_password.value.strip()

        if not u or not p:
            snack("❌ Username and Password are required")
            return

        success = add_user(u, p, new_role.value)

        if success:
            snack(f"✅ User '{u}' added successfully")
            new_username.value = ""
            new_password.value = ""
            new_role.value     = "Staff"
            load_users()
        else:
            snack("❌ Failed to add user")

        page.update()

    # ---------- User list ----------

    users_col = ft.Column(spacing=8)

    def toggle_status(uname, current_status):
        def handler(e):
            new_status = "Inactive" if current_status == "Active" else "Active"
            success = update_user_status(uname, new_status)
            if success:
                snack(f"✅ {uname} set to {new_status}")
                load_users()
            else:
                snack("❌ Failed to update status")
        return handler

    def load_users():
        users_col.controls.clear()
        records = get_all_users()

        if not records:
            users_col.controls.append(ft.Text("No users found.", color=ft.colors.GREY))
        else:
            for u in records:
                uname   = str(u.get("Username", ""))
                urole   = str(u.get("Role", ""))
                ustatus = str(u.get("Status", ""))
                is_active = ustatus == "Active"

                users_col.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Row([
                                ft.Icon(
                                    ft.icons.ADMIN_PANEL_SETTINGS if urole == "Admin"
                                    else ft.icons.PERSON,
                                    color=ft.colors.BLUE if urole == "Admin"
                                    else ft.colors.GREY,
                                ),
                                ft.Column([
                                    ft.Text(uname, weight=ft.FontWeight.BOLD, size=15),
                                    ft.Text(f"Role: {urole}  |  Status: {ustatus}",
                                            size=12, color=ft.colors.GREY),
                                ], expand=True, spacing=2),
                                ft.Switch(
                                    value=is_active,
                                    on_change=toggle_status(uname, ustatus),
                                    active_color=ft.colors.GREEN,
                                    tooltip="Toggle Active/Inactive",
                                ),
                            ], spacing=10),
                        )
                    )
                )

        page.update()

    load_users()

    # ---------- Layout ----------

    page.add(

        ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=go_back),
            ft.Text("User Management", size=22, weight=ft.FontWeight.BOLD),
        ]),

        ft.Text(f"Logged in as: {username}", size=14),
        ft.Text("Only Active users can login.", size=12, color=ft.colors.GREY),

        ft.Divider(),

        ft.Text("➕  Add New User", size=16, weight=ft.FontWeight.BOLD),

        new_username,
        new_password,
        new_role,

        ft.FilledButton(
            "ADD USER",
            width=FIELD_WIDTH,
            height=46,
            on_click=add_user_clicked,
            icon=ft.icons.PERSON_ADD,
        ),

        ft.Divider(),

        ft.Text("👥  All Users", size=16, weight=ft.FontWeight.BOLD),

        users_col,

        ft.Container(height=20),
    )

    page.update()
