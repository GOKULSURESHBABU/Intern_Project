import os

JWT_SECRET = os.getenv("JWT_SECRET", "expense-tracker-secret-key")
JWT_ALGORITHM = "HS256"

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_SENDER = os.getenv("SMTP_SENDER", "your-email@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-email-password")
