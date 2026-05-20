from datetime import datetime, timedelta
from utils import ensure_storage, load_json_file, save_json_file, hash_password, verify_password, create_jwt, send_email, USER_STORAGE


ensure_storage()


def register_user(name: str, email: str, password: str) -> tuple[bool, str]:
    users = load_json_file(USER_STORAGE)
    email = email.strip().lower()
    if any(user["email"] == email for user in users):
        return False, "Email already registered."

    new_user = {
        "name": name.strip(),
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.utcnow().isoformat()
    }
    users.append(new_user)
    save_json_file(USER_STORAGE, users)

    subject = "Welcome to Expense Tracker"
    body = f"Hello {new_user['name']},\n\nThank you for registering for the Expense Tracker app. Your account is ready to use.\n\nBest regards,\nExpense Tracker Team"
    send_email(email, subject, body)
    return True, "Registration successful. A welcome email was sent if SMTP is configured."


def authenticate_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    users = load_json_file(USER_STORAGE)
    email = email.strip().lower()
    for user in users:
        if user["email"] == email and verify_password(password, user["password"]):
            payload = {
                "name": user["name"],
                "email": user["email"],
                "iat": datetime.utcnow().timestamp(),
                "exp": (datetime.utcnow() + timedelta(hours=12)).timestamp()
            }
            token = create_jwt(payload)
            return True, token, payload
    return False, "Invalid email or password.", None
