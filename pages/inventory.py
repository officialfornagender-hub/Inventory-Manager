import flet as ft
from database import save_product
from datetime import date
import base64
import threading
import cv2

FIELD_WIDTH   = 380
BUTTON_WIDTH  = 380
BUTTON_HEIGHT = 50


# =====================================================
# HTML PAGE — Voice + Barcode Scanner (Browser-based)
# Same approach as your Flask app.py
# Uses webkitSpeechRecognition + html5-qrcode library
# =====================================================

def make_webview_html(mode: str) -> str:
    """
    mode = 'barcode'  → shows barcode scanner
    mode = 'dom'      → shows voice input for DOM
    mode = 'doe'      → shows voice input for DOE
    """

    if mode == "barcode":
        body = """
        <h2 style="color:#0078d7">📷 Scan Barcode</h2>
        <p>Point your camera at the barcode</p>
        <div id="reader" style="width:300px; margin:auto;"></div>
        <p id="result" style="color:green; font-size:18px; font-weight:bold;"></p>

        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
        const html5QrCode = new Html5Qrcode("reader");
        html5QrCode.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: 250 },
            (decodedText) => {
                document.getElementById("result").innerText = "✅ Scanned: " + decodedText;
                html5QrCode.stop();
                // Send result back to Flet
                window.location.href = "result://" + encodeURIComponent(decodedText);
            }
        );
        </script>
        """

    elif mode in ("dom", "doe"):
        label = "DOM (Date of Manufacturing)" if mode == "dom" else "DOE (Date of Expiry)"
        body = f"""
        <h2 style="color:#0078d7">🎤 Speak {label}</h2>
        <p>Say the date clearly e.g. <b>"15 June 2025"</b></p>
        <button onclick="startListening()"
            style="background:#0078d7;color:white;padding:14px 28px;
                   border:none;border-radius:8px;font-size:16px;cursor:pointer;">
            🎤 Tap to Speak
        </button>
        <p id="status" style="color:grey; margin-top:12px;">Tap button and speak...</p>
        <p id="result" style="color:green; font-size:20px; font-weight:bold;"></p>

        <script>
        function convertToDate(text) {{
            const months = {{
                "january":1,"jan":1,"february":2,"feb":2,
                "march":3,"mar":3,"april":4,"apr":4,"may":5,
                "june":6,"jun":6,"july":7,"jul":7,
                "august":8,"aug":8,"september":9,"sep":9,"sept":9,
                "october":10,"oct":10,"november":11,"nov":11,
                "december":12,"dec":12
            }};

            text = text.toLowerCase().trim();

            // Pattern: "15 june 2025" or "june 15 2025"
            let m = text.match(/(\\d{{1,2}})\\s+([a-z]+)\\s+(\\d{{4}})/);
            if (!m) m = text.match(/([a-z]+)\\s+(\\d{{1,2}})\\s+(\\d{{4}})/);

            if (m) {{
                let day, month, year;
                if (!isNaN(m[1])) {{
                    day = parseInt(m[1]);
                    month = months[m[2]] || 0;
                    year = parseInt(m[3]);
                }} else {{
                    month = months[m[1]] || 0;
                    day = parseInt(m[2]);
                    year = parseInt(m[3]);
                }}
                if (day && month && year) {{
                    return String(day).padStart(2,'0') + '-' +
                           String(month).padStart(2,'0') + '-' + year;
                }}
            }}

            // Fallback: try JS Date parse
            const d = new Date(text);
            if (!isNaN(d)) {{
                let dd = String(d.getDate()).padStart(2,'0');
                let mm = String(d.getMonth()+1).padStart(2,'0');
                let yyyy = d.getFullYear();
                return dd + '-' + mm + '-' + yyyy;
            }}
            return "";
        }}

        function startListening() {{
            const recognition = new (window.SpeechRecognition ||
                                     window.webkitSpeechRecognition)();
            recognition.lang = "en-IN";
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            document.getElementById("status").innerText = "🎙 Listening...";

            recognition.start();

            recognition.onresult = function(event) {{
                const spoken = event.results[0][0].transcript;
                document.getElementById("status").innerText = "Heard: " + spoken;
                const parsed = convertToDate(spoken);
                if (parsed) {{
                    document.getElementById("result").innerText = "✅ Date: " + parsed;
                    // Send result back to Flet
                    window.location.href = "result://" + encodeURIComponent(parsed);
                }} else {{
                    document.getElementById("status").innerText =
                        "❓ Could not parse '" + spoken + "'. Try again.";
                }}
            }};

            recognition.onerror = function(event) {{
                document.getElementById("status").innerText = "❌ Error: " + event.error;
            }};
        }}
        </script>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            text-align: center;
            padding: 20px;
        }}
    </style>
    </head>
    <body>
    {body}
    </body>
    </html>
    """


# =====================================================
# SHOW INVENTORY (ADD PRODUCT)
# =====================================================

def show_inventory(page: ft.Page):

    page.clean()
    page.title  = "Add New Product"
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    user     = page.session.get("user") or {}
    username = user.get("Username", "Unknown")
    role     = user.get("Role", "Staff")

    captured_image_base64 = {"value": None}
    webview_mode          = {"value": None}   # track what webview is open for

    # ---------- Controls ----------

    cno = ft.TextField(label="C.NO", width=FIELD_WIDTH, prefix_icon=ft.icons.TAG)

    barcode_field = ft.TextField(
        label="Barcode / EAN",
        width=280,
        prefix_icon=ft.icons.QR_CODE,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    condition = ft.Dropdown(
        label="Condition",
        width=FIELD_WIDTH,
        value="Normal",
        options=[
            ft.dropdown.Option("Normal"),
            ft.dropdown.Option("Tester"),
            ft.dropdown.Option("Damage"),
        ],
    )

    dom = ft.TextField(
        label="DOM (DD-MM-YYYY)",
        width=200,
        prefix_icon=ft.icons.CALENDAR_TODAY,
        hint_text="01-01-2025",
    )

    doe = ft.TextField(
        label="DOE (DD-MM-YYYY)",
        width=200,
        prefix_icon=ft.icons.EVENT,
        hint_text="01-01-2026",
    )

    description = ft.TextField(
        label="Description",
        width=FIELD_WIDTH,
        multiline=True,
        min_lines=3,
        visible=False,
    )

    photo_preview = ft.Image(
        width=300, height=200,
        fit=ft.ImageFit.CONTAIN,
        border_radius=10,
        visible=False,
    )

    photo_status = ft.Text("No Image Selected", color=ft.colors.GREY, size=13, visible=False)
    scan_status  = ft.Text("", size=12, color=ft.colors.BLUE, italic=True)
    voice_status = ft.Text("", size=12, color=ft.colors.BLUE, italic=True)
    status_msg   = ft.Text("", size=13, color=ft.colors.GREEN)

    photo_btn = ft.ElevatedButton(
        "📷  Capture Photo", width=FIELD_WIDTH, visible=False, icon=ft.icons.CAMERA_ALT,
    )
    retake_btn = ft.OutlinedButton(
        "🔄  Retake Photo", width=FIELD_WIDTH, visible=False, icon=ft.icons.REPLAY,
    )

    # =====================================================
    # WEBVIEW DIALOG — for barcode scan and voice input
    # Same as Flask app's browser-based JS approach
    # =====================================================

    webview_container = ft.Column(visible=False, width=FIELD_WIDTH)
    webview_close_btn = ft.TextButton("✖  Close", visible=False)

    current_webview = {"ctrl": None}

    def on_webview_navigate(e):
        """Catch result:// URLs sent from JS back to Flet."""
        url = e.url if hasattr(e, "url") else str(e)

        if "result://" in url:
            import urllib.parse
            value = urllib.parse.unquote(url.split("result://")[1])
            mode  = webview_mode["value"]

            if mode == "barcode":
                barcode_field.value = value
                scan_status.value   = f"✅ Scanned: {value}"
            elif mode == "dom":
                dom.value         = value
                voice_status.value = f"✅ DOM set to: {value}"
            elif mode == "doe":
                doe.value         = value
                voice_status.value = f"✅ DOE set to: {value}"

            close_webview(None)
            page.update()

    def open_webview(mode: str):
        webview_mode["value"] = mode
        html_content = make_webview_html(mode)

        wv = ft.WebView(
            url="about:blank",
            expand=True,
            height=420,
            on_page_started=on_webview_navigate,
            on_page_ended=on_webview_navigate,
            on_url_change=on_webview_navigate,
            javascript_enabled=True,
        )
        # Load HTML directly
        wv.url = f"data:text/html;charset=utf-8,{html_content}"
        current_webview["ctrl"] = wv

        webview_container.controls = [wv]
        webview_container.visible  = True
        webview_close_btn.visible  = True
        page.update()

    def close_webview(e):
        webview_container.controls  = []
        webview_container.visible   = False
        webview_close_btn.visible   = False
        current_webview["ctrl"]     = None
        webview_mode["value"]       = None
        page.update()

    webview_close_btn.on_click = close_webview

    # =====================================================
    # PHOTO CAPTURE — OpenCV (no extra pip needed,
    # opencv-python is usually already installed with flet)
    # =====================================================

    def run_camera_capture():
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                photo_status.value = "❌ Camera not found."
                page.update()
                return

            captured_frame = None
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.putText(frame, "SPACE=Capture  ESC=Cancel",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,220,0), 2)
                cv2.imshow("📷 Capture Photo", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == 32:
                    captured_frame = frame.copy()
                    break
                elif key == 27:
                    break

            cap.release()
            cv2.destroyAllWindows()

            if captured_frame is not None:
                _, buf  = cv2.imencode(".jpg", captured_frame)
                img_b64 = base64.b64encode(buf).decode("utf-8")
                captured_image_base64["value"] = img_b64
                photo_preview.src_base64 = img_b64
                photo_preview.visible    = True
                photo_btn.visible        = False
                retake_btn.visible       = True
                photo_status.value       = "✅ Photo captured!"
            else:
                photo_status.value = "❌ Cancelled."

        except Exception as ex:
            photo_status.value = f"❌ Error: {str(ex)}"

        page.update()

    def open_camera_capture(e):
        photo_status.value = "📷 Opening camera... SPACE=Capture  ESC=Cancel"
        page.update()
        threading.Thread(target=run_camera_capture, daemon=True).start()

    def retake_photo(e):
        photo_preview.visible          = False
        photo_preview.src_base64       = None
        photo_btn.visible              = True
        retake_btn.visible             = False
        photo_status.value             = "No Image Selected"
        captured_image_base64["value"] = None
        page.update()

    photo_btn.on_click  = open_camera_capture
    retake_btn.on_click = retake_photo

    # =====================================================
    # DATE PICKER — Calendar (Flet native)
    # =====================================================

    def dom_picked(e):
        if dom_picker.value:
            dom.value = dom_picker.value.strftime("%d-%m-%Y")
            page.update()

    def doe_picked(e):
        if doe_picker.value:
            doe.value = doe_picker.value.strftime("%d-%m-%Y")
            page.update()

    dom_picker = ft.DatePicker(first_date=date(2000,1,1), last_date=date(2100,12,31), on_change=dom_picked)
    doe_picker = ft.DatePicker(first_date=date(2000,1,1), last_date=date(2100,12,31), on_change=doe_picked)
    page.overlay.extend([dom_picker, doe_picker])

    def open_dom_picker(e):
        dom_picker.open = True
        page.update()

    def open_doe_picker(e):
        doe_picker.open = True
        page.update()

    # =====================================================
    # CONDITION CHANGE
    # =====================================================

    def condition_changed(e):
        is_special = condition.value != "Normal"
        description.visible   = is_special
        photo_status.visible  = is_special
        photo_btn.visible     = is_special and captured_image_base64["value"] is None
        retake_btn.visible    = is_special and captured_image_base64["value"] is not None
        photo_preview.visible = is_special and captured_image_base64["value"] is not None
        if condition.value == "Tester":
            description.label = "Tester Description"
        elif condition.value == "Damage":
            description.label = "Damage Description"
        page.update()

    condition.on_change = condition_changed

    # =====================================================
    # SNACK / RESET / SAVE
    # =====================================================

    def snack(msg):
        page.snack_bar      = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()

    def reset_form(e=None):
        for f in [cno, barcode_field, dom, doe, description]:
            f.value = ""
        condition.value = "Normal"
        for c in [description, photo_status, photo_btn, retake_btn, photo_preview]:
            c.visible = False
        photo_preview.src_base64       = None
        captured_image_base64["value"] = None
        status_msg.value               = ""
        voice_status.value             = ""
        scan_status.value              = ""
        close_webview(None)
        page.update()

    def save_clicked(e):
        if not cno.value.strip():
            snack("❌ Please enter C.NO"); return
        if not barcode_field.value.strip():
            snack("❌ Please enter Barcode"); return
        if not dom.value.strip():
            snack("❌ Please enter DOM"); return
        if not doe.value.strip():
            snack("❌ Please enter DOE"); return
        if condition.value != "Normal" and not description.value.strip():
            snack("❌ Please enter Description"); return

        success = save_product(
            cno.value.strip(),
            barcode_field.value.strip(),
            condition.value,
            description.value.strip(),
            dom.value.strip(),
            doe.value.strip(),
            captured_image_base64["value"] or "",
            username,
        )
        if success:
            snack("✅ Product Saved Successfully")
            reset_form()
        else:
            snack("❌ Failed to Save Product")

    def go_back(e):
        from pages.dashboard import show_dashboard
        show_dashboard(page)

    # =====================================================
    # LAYOUT
    # =====================================================

    page.add(

        ft.Row([
            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=go_back),
            ft.Text("Add New Product", size=22, weight=ft.FontWeight.BOLD),
        ]),
        ft.Text(f"Welcome, {username}", size=15),
        ft.Text(f"Role : {role}", size=13, color=ft.colors.GREY),

        ft.Divider(),

        cno,

        # Barcode + Scanner
        ft.Text("Barcode / EAN", size=12, color=ft.colors.GREY),
        ft.Row([
            barcode_field,
            ft.IconButton(
                icon=ft.icons.QR_CODE_SCANNER,
                tooltip="Open camera to scan barcode",
                on_click=lambda e: open_webview("barcode"),
                icon_color=ft.colors.BLUE,
                icon_size=28,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER),
        scan_status,

        condition,

        # DOM — Calendar + Voice
        ft.Text("Date of Manufacturing (DOM)", size=12, color=ft.colors.GREY),
        ft.Row([
            dom,
            ft.IconButton(
                icon=ft.icons.CALENDAR_MONTH,
                tooltip="Pick DOM from calendar",
                on_click=open_dom_picker,
                icon_color=ft.colors.BLUE,
                icon_size=26,
            ),
            ft.IconButton(
                icon=ft.icons.MIC,
                tooltip="Speak DOM date",
                on_click=lambda e: open_webview("dom"),
                icon_color=ft.colors.RED,
                icon_size=26,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER),

        # DOE — Calendar + Voice
        ft.Text("Date of Expiry (DOE)", size=12, color=ft.colors.GREY),
        ft.Row([
            doe,
            ft.IconButton(
                icon=ft.icons.CALENDAR_MONTH,
                tooltip="Pick DOE from calendar",
                on_click=open_doe_picker,
                icon_color=ft.colors.BLUE,
                icon_size=26,
            ),
            ft.IconButton(
                icon=ft.icons.MIC,
                tooltip="Speak DOE date",
                on_click=lambda e: open_webview("doe"),
                icon_color=ft.colors.RED,
                icon_size=26,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER),

        voice_status,

        # WebView panel (appears when scanner/voice opened)
        ft.Container(height=8),
        webview_close_btn,
        webview_container,
        ft.Container(height=8),

        description,
        photo_status,
        photo_preview,
        photo_btn,
        retake_btn,

        ft.Divider(),
        status_msg,

        ft.FilledButton("💾  SAVE",      width=BUTTON_WIDTH, height=BUTTON_HEIGHT, on_click=save_clicked),
        ft.ElevatedButton("➕  NEW ENTRY", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, on_click=reset_form),
        ft.OutlinedButton("🧹  RESET",    width=BUTTON_WIDTH, height=BUTTON_HEIGHT, on_click=reset_form),

        ft.Container(height=20),
    )

    page.update()
