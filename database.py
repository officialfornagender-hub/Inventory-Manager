import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# =====================================================
# GOOGLE SHEETS CONNECTION
# =====================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(
    "inventory-manager.json",
    scopes=SCOPES,
)

client = gspread.authorize(creds)

spreadsheet = client.open("Inventory Manager Database")

users_sheet     = spreadsheet.worksheet("Users")
inventory_sheet = spreadsheet.worksheet("Inventory")
audit_sheet     = spreadsheet.worksheet("Audit")


# =====================================================
# GET NEXT SR.NO
# =====================================================

def get_next_srno():

    data = inventory_sheet.get_all_values()

    if len(data) <= 1:
        return 1

    return len(data)


# =====================================================
# CALCULATE STATUS
# =====================================================

def calculate_status(doe):

    try:

        expiry_date = datetime.strptime(doe, "%d-%m-%Y").date()

        today = date.today()

        days_left = (expiry_date - today).days

        if days_left > 180:
            return "Saleable"

        elif days_left > 0:
            return "Near to Expiry"

        else:
            return "Expired"

    except Exception:
        return "Unknown"


# =====================================================
# UPDATE ALL STATUS
# =====================================================

def update_all_status():

    records = inventory_sheet.get_all_records()

    for row_no, row in enumerate(records, start=2):

        try:

            new_status     = calculate_status(str(row["DOE"]))
            current_status = str(row["Status"])

            if new_status != current_status:
                inventory_sheet.update_cell(row_no, 8, new_status)

        except Exception as e:
            print(f"Row {row_no} Error : {e}")


# =====================================================
# SAVE PRODUCT
# =====================================================

def save_product(cno, barcode, condition, description, dom, doe, picture, entered_by):

    try:

        srno       = get_next_srno()
        status     = calculate_status(doe)
        entry_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        inventory_sheet.append_row([
            srno,
            cno,
            barcode,
            condition,
            description,
            dom,
            doe,
            status,
            picture,
            entered_by,
            entry_date,
            "",
            "",
        ])

        return True

    except Exception as e:
        print(e)
        return False


# =====================================================
# GET PRODUCT BY BARCODE
# =====================================================

def get_product(barcode):

    records = inventory_sheet.get_all_records()

    for row in records:
        if str(row["Barcode"]) == str(barcode):
            return row

    return None


# =====================================================
# SEARCH PRODUCTS
# =====================================================

def search_products(search_by, value):

    records = inventory_sheet.get_all_records()

    value   = value.strip().lower()
    results = []

    for row in records:

        if search_by == "All Fields":
            for item in row.values():
                if value in str(item).lower():
                    results.append(row)
                    break
        else:
            if value in str(row.get(search_by, "")).lower():
                results.append(row)

    return results


# =====================================================
# UPDATE PRODUCT
# =====================================================

def update_product(barcode, cno, condition, description, dom, doe, picture, edited_by):

    records = inventory_sheet.get_all_records()

    for row_no, row in enumerate(records, start=2):

        if str(row["Barcode"]) == str(barcode):

            status       = calculate_status(doe)
            last_updated = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            inventory_sheet.update(
                f"B{row_no}:M{row_no}",
                [[
                    cno,
                    barcode,
                    condition,
                    description,
                    dom,
                    doe,
                    status,
                    picture,
                    row["Entered By"],
                    row["Entry Date"],
                    edited_by,
                    last_updated,
                ]]
            )

            return True

    return False


# =====================================================
# DELETE PRODUCT BY BARCODE
# =====================================================

def delete_product_by_barcode(barcode):

    records = inventory_sheet.get_all_records()

    for row_no, row in enumerate(records, start=2):

        if str(row["Barcode"]) == str(barcode):
            inventory_sheet.delete_rows(row_no)
            return True

    return False


# =====================================================
# GET ALL INVENTORY RECORDS
# =====================================================

def get_all_inventory():
    return inventory_sheet.get_all_records()


# =====================================================
# GET ALL USERS
# =====================================================

def get_all_users():
    return users_sheet.get_all_records()


# =====================================================
# ADD USER
# =====================================================

def add_user(username, password, role):

    try:
        users_sheet.append_row([username, password, role, "Active"])
        return True
    except Exception as e:
        print(e)
        return False


# =====================================================
# UPDATE USER STATUS
# =====================================================

def update_user_status(username, status):

    records = users_sheet.get_all_records()

    for row_no, row in enumerate(records, start=2):
        if str(row["Username"]) == str(username):
            users_sheet.update_cell(row_no, 4, status)
            return True

    return False


# =====================================================
# LOG AUDIT
# =====================================================

def log_audit(action, performed_by, details=""):

    try:
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        audit_sheet.append_row([timestamp, performed_by, action, details])
    except Exception as e:
        print(f"Audit log error: {e}")


# =====================================================
# TEST CONNECTION
# =====================================================

if __name__ == "__main__":
    print("Connected Successfully")
    update_all_status()
    print("Status Updated Successfully")
