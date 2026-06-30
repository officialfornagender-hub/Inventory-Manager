import flet as ft
from database import update_product, delete_product_by_barcode

FIELD_WIDTH = 340


# =====================================================
# SHOW PRODUCT VIEW
# =====================================================

def show_product_view(page: ft.Page, product: dict):

    page.clean()
    page.title  = "Product Details"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    user     = page.session.get("user") or {}
    username = user.get("Username", "Unknown")
    role     = user.get("Role", "Staff")

    is_editing = ft.Ref[bool]()
    is_editing.current = False

    # ---------- Helpers ----------

    def val(key):
        return str(product.get(key, ""))

    def status_color(status):
        return {
            "Saleable":       ft.colors.GREEN,
            "Near to Expiry": ft.colors.ORANGE,
            "Expired":        ft.colors.RED,
        }.get(status, ft.colors.GREY)

    def snack(msg):
        page.snack_bar      = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    # ---------- Read-only info rows ----------

    def info_tile(label, value, color=None):
        return ft.ListTile(
            title=ft.Text(label, size=13, color=ft.colors.GREY),
            subtitle=ft.Text(value, size=15, color=color),
            dense=True,
        )

    # ---------- Edit fields (hidden by default) ----------

    edit_cno = ft.TextField(
        label="C.NO",
        value=val("C.NO"),
        width=FIELD_WIDTH,
        visible=False,
    )

    edit_condition = ft.Dropdown(
        label="Condition",
        value=val("Condition"),
        width=FIELD_WIDTH,
        visible=False,
        options=[
            ft.dropdown.Option("Normal"),
            ft.dropdown.Option("Tester"),
            ft.dropdown.Option("Damage"),
        ],
    )

    edit_description = ft.TextField(
        label="Description",
        value=val("Description"),
        width=FIELD_WIDTH,
        multiline=True,
        min_lines=2,
        visible=False,
    )

    edit_dom = ft.TextField(
        label="DOM (DD-MM-YYYY)",
        value=val("DOM"),
        width=FIELD_WIDTH,
        visible=False,
    )

    edit_doe = ft.TextField(
        label="DOE (DD-MM-YYYY)",
        value=val("DOE"),
        width=FIELD_WIDTH,
        visible=False,
    )

    # Status badge
    status_badge = ft.Container(
        content=ft.Text(val("Status"), size=12, color=ft.colors.WHITE),
        bgcolor=status_color(val("Status")),
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
        border_radius=12,
    )

    # Buttons
    edit_btn   = ft.ElevatedButton("✏  EDIT",   width=FIELD_WIDTH, icon=ft.icons.EDIT)
    save_btn   = ft.FilledButton("💾  SAVE",    width=FIELD_WIDTH, visible=False)
    cancel_btn = ft.OutlinedButton("✖  CANCEL", width=FIELD_WIDTH, visible=False)
    delete_btn = ft.ElevatedButton(
        "🗑  DELETE",
        width=FIELD_WIDTH,
        color=ft.colors.RED,
        icon=ft.icons.DELETE,
    )
    back_btn = ft.OutlinedButton("⬅  BACK", width=FIELD_WIDTH, icon=ft.icons.ARROW_BACK)

    # ---------- Events ----------

    def go_back(e):
        from pages.product_management import show_product_management
        show_product_management(page)

    def enable_edit(e):
        edit_cno.visible         = True
        edit_condition.visible   = True
        edit_description.visible = True
        edit_dom.visible         = True
        edit_doe.visible         = True
        edit_btn.visible         = False
        save_btn.visible         = True
        cancel_btn.visible       = True
        page.update()

    def cancel_edit(e):
        edit_cno.visible         = False
        edit_condition.visible   = False
        edit_description.visible = False
        edit_dom.visible         = False
        edit_doe.visible         = False
        edit_btn.visible         = True
        save_btn.visible         = False
        cancel_btn.visible       = False
        page.update()

    def save_edit(e):

        if not edit_cno.value.strip():
            snack("❌ C.NO cannot be empty")
            return

        if not edit_dom.value.strip() or not edit_doe.value.strip():
            snack("❌ DOM and DOE cannot be empty")
            return

        success = update_product(
            barcode=val("Barcode"),
            cno=edit_cno.value.strip(),
            condition=edit_condition.value,
            description=edit_description.value.strip(),
            dom=edit_dom.value.strip(),
            doe=edit_doe.value.strip(),
            picture="",
            edited_by=username,
        )

        if success:
            snack("✅ Product Updated Successfully")
            # Update local product dict so info shows latest
            product["C.NO"]        = edit_cno.value.strip()
            product["Condition"]   = edit_condition.value
            product["Description"] = edit_description.value.strip()
            product["DOM"]         = edit_dom.value.strip()
            product["DOE"]         = edit_doe.value.strip()
            product["Edited By"]   = username
            show_product_view(page, product)
        else:
            snack("❌ Failed to Update Product")

    def confirm_delete(e):

        def do_delete(e):
            dlg.open = False
            page.update()
            success = delete_product_by_barcode(val("Barcode"))
            if success:
                snack("✅ Product Deleted")
                from pages.product_management import show_product_management
                show_product_management(page)
            else:
                snack("❌ Failed to Delete Product")

        def cancel_delete(e):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Delete Barcode {val('Barcode')}? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.FilledButton("DELETE", on_click=do_delete,
                                style=ft.ButtonStyle(bgcolor=ft.colors.RED)),
            ],
        )
        page.dialog      = dlg
        dlg.open         = True
        page.update()

    edit_btn.on_click   = enable_edit
    save_btn.on_click   = save_edit
    cancel_btn.on_click = cancel_edit
    delete_btn.on_click = confirm_delete
    back_btn.on_click   = go_back

    # ---------- Layout ----------

    page.add(

        ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=go_back),
            ft.Text("Product Details", size=22, weight=ft.FontWeight.BOLD),
        ]),

        ft.Divider(),

        # Status badge
        ft.Row([status_badge], alignment=ft.MainAxisAlignment.CENTER),

        ft.Container(height=8),

        # Product info
        ft.Text("📦  Product Information", size=16, weight=ft.FontWeight.BOLD),

        info_tile("C.NO",        val("C.NO")),
        info_tile("Barcode",     val("Barcode")),
        info_tile("Condition",   val("Condition")),
        info_tile("Description", val("Description")),
        info_tile("DOM",         val("DOM")),
        info_tile("DOE",         val("DOE")),
        info_tile("Status",      val("Status"), status_color(val("Status"))),

        ft.Divider(),

        # Audit info
        ft.Text("👤  Audit Information", size=16, weight=ft.FontWeight.BOLD),

        info_tile("Entered By",   val("Entered By")),
        info_tile("Entry Date",   val("Entry Date")),
        info_tile("Edited By",    val("Edited By")),
        info_tile("Last Updated", val("Last Updated")),

        ft.Divider(),

        # Product image placeholder
        ft.Text("📷  Product Image", size=16, weight=ft.FontWeight.BOLD),

        ft.Container(
            width=300,
            height=180,
            border=ft.border.all(1, ft.colors.GREY_300),
            border_radius=10,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED, size=40, color=ft.colors.GREY),
                    ft.Text("No Image Available", color=ft.colors.GREY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ),

        ft.Divider(),

        # Edit fields (shown when editing)
        ft.Text("✏  Edit Product", size=16, weight=ft.FontWeight.BOLD),
        edit_cno,
        edit_condition,
        edit_description,
        edit_dom,
        edit_doe,

        ft.Container(height=8),

        # Action buttons
        edit_btn,
        save_btn,
        cancel_btn,

        ft.Container(height=8),

        delete_btn if role == "Admin" else ft.Container(),

        ft.Container(height=8),

        back_btn,

        ft.Container(height=20),
    )

    page.update()
