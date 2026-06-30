from database import users_sheet


# =====================================================
# LOGIN
# =====================================================

def login(username, password):

    records = users_sheet.get_all_records()

    for user in records:

        if (
            str(user["Username"]) == str(username)
            and str(user["Password"]) == str(password)
            and str(user["Status"]) == "Active"
        ):
            return user

    return None
