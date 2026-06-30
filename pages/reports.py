import flet as ft
from database import get_all_inventory
from collections import Counter


# =====================================================
# SHOW REPORTS
# =====================================================

def show_reports(page: ft.Page):

    page.clean()
    page.title  = "Reports"
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
            ft.Text("Reports", size=22, weight=ft.FontWeight.BOLD),
        ]),
        ft.Divider(),
        ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
    )
    page.update()

    records = get_all_inventory()

    # ---------- Statistics ----------

    total     = len(records)
    statuses  = Counter(str(r.get("Status", "Unknown")) for r in records)
    condition = Counter(str(r.get("Condition", "Unknown")) for r in records)
    by_user   = Counter(str(r.get("Entered By", "Unknown")) for r in records)

    saleable    = statuses.get("Saleable", 0)
    near_expiry = statuses.get("Near to Expiry", 0)
    expired     = statuses.get("Expired", 0)

    page.clean()

    # ---------- Summary card builder ----------

    def stat_card(label, value, color=ft.colors.BLUE, icon=ft.icons.INFO):
        return ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Row([
                    ft.Icon(icon, color=color, size=36),
                    ft.Column([
                        ft.Text(str(value), size=26, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(label, size=13, color=ft.colors.GREY),
                    ], spacing=2),
                ], spacing=16),
            )
        )

    # ---------- Table builder ----------

    def summary_table(title, data_dict, col1="Category", col2="Count"):
        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(k))),
                ft.DataCell(ft.Text(str(v))),
            ])
            for k, v in data_dict.items()
        ]
        return ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text(col1, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text(col2, weight=ft.FontWeight.BOLD), numeric=True),
                ],
                rows=rows,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=8,
                column_spacing=40,
            ),
        ], spacing=8)

    # ---------- Layout ----------

    page.add(

        ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=go_back),
            ft.Text("Reports", size=22, weight=ft.FontWeight.BOLD),
        ]),

        ft.Text(f"Welcome, {username}", size=15),
        ft.Text("Inventory Summary Report", size=13, color=ft.colors.GREY),

        ft.Divider(),

        # KPI cards
        stat_card("Total Products",    total,       ft.colors.BLUE,   ft.icons.INVENTORY_2),
        stat_card("Saleable",          saleable,    ft.colors.GREEN,  ft.icons.CHECK_CIRCLE),
        stat_card("Near to Expiry",    near_expiry, ft.colors.ORANGE, ft.icons.WARNING_AMBER),
        stat_card("Expired",           expired,     ft.colors.RED,    ft.icons.CANCEL),

        ft.Divider(),

        # Status breakdown
        summary_table("📊 Status Breakdown", dict(statuses), "Status", "Count"),

        ft.Container(height=16),

        # Condition breakdown
        summary_table("🔧 Condition Breakdown", dict(condition), "Condition", "Count"),

        ft.Container(height=16),

        # Top users
        summary_table(
            "👤 Entries by User",
            dict(by_user.most_common(10)),
            "Entered By",
            "Products",
        ),

        ft.Container(height=20),
    )

    page.update()
