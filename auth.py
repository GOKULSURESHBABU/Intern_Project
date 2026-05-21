import os
import json
import streamlit as st
from datetime import datetime, timedelta
from utils import ensure_storage, load_json_file, save_json_file, hash_password, verify_password, create_jwt, send_email, USER_STORAGE
from streamlit_google_auth import Authenticate

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


# --- GOOGLE OAUTH FLOW HANDLING ---
def render_google_login():
    # 1. Structure credentials dynamically in the format the library demands
    google_secrets = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [os.getenv("REDIRECT_URI")]
        }
    }
    
    # 2. Write to a temporary file for the underlying package parser
    secrets_path = "google_creds_temp.json"
    with open(secrets_path, "w") as f:
        json.dump(google_secrets, f)

    # 3. Securely initiate the OAuth handler interface (With redirect_uri parameter)
    auth = Authenticate(
        secret_credentials_path=secrets_path, 
        cookie_name="google_user_cookie",
        cookie_key="some_random_secret_key",
        cookie_expiry_days=1,
        redirect_uri=os.getenv("REDIRECT_URI")  # Fixes the missing argument error
    )
    
    auth.check_authentification()
    
    if not st.session_state.get("connected", False):
        auth.login()
    else:
        # Clean up config artifacts upon validation loop completion
        if os.path.exists(secrets_path):
            os.remove(secrets_path)
            
        return {
            "name": st.session_state.get("name"),
            "email": st.session_state.get("email")
        }
    return None