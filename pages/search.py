import flet as ft
from database import get_all_inventory


# =====================================================
# SHOW EXPIRY ALERTS
# =====================================================

def show_expiry_alerts(page: ft.Page):

    page.clean()
    page.title  = "Expiry Alerts"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    user     = page.session.get("user") or {}
    username = user.get("Username", "Unknown")

    def go_back(e):
        from pages.dashboard import show_dashboard
        show_dashboard(page)

    # ---------- Load data ----------

    loading = ft.ProgressRing()
    page.add(
        ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=go_back),
            ft.Text("Expiry Alerts", size=22, weight=ft.FontWeight.BOLD),
        ]),
        ft.Divider(),
        ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
    )
    page.update()

    records = get_all_inventory()

    expired       = [r for r in records if str(r.get("Status", "")) == "Expired"]
    near_expiry   = [r for r in records if str(r.get("Status", "")) == "Near to Expiry"]

    page.clean()

    # ---------- Card builder ----------

    def alert_card(row, badge_color):
        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            f"C.NO : {row.get('C.NO', '')}",
                            weight=ft.FontWeight.BOLD,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text(
                                str(row.get("Status", "")),
                                size=11,
                                color=ft.colors.WHITE,
                            ),
                            bgcolor=badge_color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=10,
                        ),
                    ]),
                    ft.Text(f"Barcode : {row.get('Barcode', '')}"),
                    ft.Text(f"DOE     : {row.get('DOE', '')}"),
                ], spacing=4),
            )
        )

    results = ft.Column(spacing=8)

    if not expired and not near_expiry:
        results.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.CHECK_CIRCLE, size=48, color=ft.colors.GREEN),
                    ft.Text("All products are Saleable!", size=16, color=ft.colors.GREEN),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.alignment.center,
                padding=40,
            )
        )
    else:
        if expired:
            results.controls.append(
                ft.Text(
                    f"🔴  Expired  ({len(expired)})",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.RED,
                )
            )
            for r in expired:
                results.controls.append(alert_card(r, ft.colors.RED))

        if near_expiry:
            results.controls.append(ft.Container(height=10))
            results.controls.append(
                ft.Text(
                    f"🟠  Near to Expiry  ({len(near_expiry)})",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.ORANGE,
                )
            )
            for r in near_expiry:
                results.controls.append(alert_card(r, ft.colors.ORANGE))

    page.add(
        ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=go_back),
            ft.Text("Expiry Alerts", size=22, weight=ft.FontWeight.BOLD),
        ]),
        ft.Text(f"Welcome, {username}", size=15),
        ft.Divider(),
        ft.Row([
            ft.Container(
                content=ft.Text(f"Expired: {len(expired)}", color=ft.colors.WHITE, size=13),
                bgcolor=ft.colors.RED,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border_radius=8,
            ),
            ft.Container(
                content=ft.Text(f"Near Expiry: {len(near_expiry)}", color=ft.colors.WHITE, size=13),
                bgcolor=ft.colors.ORANGE,
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border_radius=8,
            ),
        ], spacing=10),
        ft.Divider(),
        results,
        ft.Container(height=20),
    )

    page.update()
