import flet as ft
from database import search_products

FIELD_WIDTH = 380


# =====================================================
# SHOW PRODUCT MANAGEMENT
# =====================================================

def show_product_management(page: ft.Page):

    page.clean()
    page.title  = "Product Management"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    user     = page.session.get("user") or {}
    username = user.get("Username", "Unknown")
    role     = user.get("Role", "Staff")

    # ---------- Controls ----------

    search_by = ft.Dropdown(
        label="Search By",
        width=FIELD_WIDTH,
        value="Barcode",
        options=[
            ft.dropdown.Option(x)
            for x in [
                "Barcode",
                "C.NO",
                "Condition",
                "Description",
                "Status",
                "Entered By",
                "Entry Date",
                "Edited By",
                "Last Updated",
                "All Fields",
            ]
        ],
    )

    search_box  = ft.TextField(label="Enter Barcode", width=300)
    camera_btn  = ft.IconButton(icon=ft.icons.QR_CODE_SCANNER, tooltip="Scan Barcode")
    search_btn  = ft.IconButton(icon=ft.icons.SEARCH, tooltip="Search")
    results_col = ft.Column(spacing=10)
    result_count = ft.Text("", size=13, color=ft.colors.GREY)

    # ---------- Events ----------

    def search_type_changed(e):
        label = search_by.value
        search_box.label   = "Search Anything" if label == "All Fields" else f"Enter {label}"
        camera_btn.visible = label == "Barcode"
        page.update()

    search_by.on_change = search_type_changed

    def go_back(e):
        from pages.dashboard import show_dashboard
        show_dashboard(page)

    def view_product(product):
        def handler(e):
            from pages.product_view import show_product_view
            show_product_view(page, product)
        return handler

    def status_color(status):
        return {
            "Saleable":       ft.colors.GREEN,
            "Near to Expiry": ft.colors.ORANGE,
            "Expired":        ft.colors.RED,
        }.get(status, ft.colors.GREY)

    def search_clicked(e):

        results_col.controls.clear()
        keyword = search_box.value.strip()

        if not keyword:
            results_col.controls.append(ft.Text("Please enter a search value.", color=ft.colors.RED))
            result_count.value = ""
            page.update()
            return

        data = search_products(search_by.value, keyword)

        if not data:
            results_col.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.icons.SEARCH_OFF, size=40, color=ft.colors.GREY),
                            ft.Text("No Records Found", color=ft.colors.GREY, size=15),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    alignment=ft.alignment.center,
                    padding=30,
                )
            )
            result_count.value = "0 results"
        else:
            result_count.value = f"{len(data)} result(s) found"
            for row in data:
                status = str(row.get("Status", ""))
                results_col.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=12,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(
                                        f"C.NO : {row.get('C.NO', '')}",
                                        weight=ft.FontWeight.BOLD,
                                        size=15,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Text(status, size=11, color=ft.colors.WHITE),
                                        bgcolor=status_color(status),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                        border_radius=12,
                                    ),
                                ]),
                                ft.Text(f"Barcode   : {row.get('Barcode', '')}"),
                                ft.Text(f"Condition : {row.get('Condition', '')}"),
                                ft.Text(f"DOE       : {row.get('DOE', '')}"),
                                ft.Row([
                                    ft.ElevatedButton(
                                        "👁  VIEW",
                                        on_click=view_product(row),
                                        expand=True,
                                    ),
                                ]),
                            ], spacing=6),
                        )
                    )
                )

        page.update()

    search_btn.on_click = search_clicked
    search_box.on_submit = search_clicked

    # ---------- Layout ----------

    page.add(

        ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=go_back),
            ft.Text("Product Management", size=22, weight=ft.FontWeight.BOLD),
        ]),

        ft.Text(f"Welcome, {username}", size=15),
        ft.Text(f"Role : {role}", size=13, color=ft.colors.GREY),

        ft.Divider(),

        search_by,

        ft.Row(
            [search_box, camera_btn, search_btn],
            alignment=ft.MainAxisAlignment.CENTER,
        ),

        ft.Divider(),

        ft.Row([
            ft.Text("Search Results", size=17, weight=ft.FontWeight.BOLD, expand=True),
            result_count,
        ]),

        results_col,

        ft.Container(height=20),
    )

    page.update()
