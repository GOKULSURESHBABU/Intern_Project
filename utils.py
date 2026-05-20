import json
import os
import hashlib
import jwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import JWT_SECRET, JWT_ALGORITHM, SMTP_SERVER, SMTP_PORT, SMTP_SENDER, SMTP_PASSWORD

USER_STORAGE = os.path.join("storage", "users.json")
EXPENSE_STORAGE = os.path.join("storage", "expenses.json")


def ensure_storage():
    os.makedirs("storage", exist_ok=True)
    if not os.path.exists(USER_STORAGE):
        save_json_file(USER_STORAGE, [])
    if not os.path.exists(EXPENSE_STORAGE):
        save_json_file(EXPENSE_STORAGE, [])


def load_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def hash_password(password: str) -> str:
    salted = password.encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_jwt(payload: dict) -> str:
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def send_email(recipient: str, subject: str, body: str) -> bool:
    try:
        message = MIMEMultipart()
        message["From"] = SMTP_SENDER
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        context = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        context.starttls()
        context.login(SMTP_SENDER, SMTP_PASSWORD)
        context.sendmail(SMTP_SENDER, recipient, message.as_string())
        context.quit()
        return True
    except Exception:
        return False


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def parse_date(date_text: str) -> str:
    try:
        parsed = datetime.fromisoformat(date_text)
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d")
