import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    EMAIL_USER = os.getenv("EMAIL_USER")
    # EMAIL_PASSWORD used only for basic auth (deprecated for many accounts)
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") 
    
    # OAuth2 Settings
    CLIENT_ID = os.getenv("CLIENT_ID")
    AUTHORITY = "https://login.microsoftonline.com/common"
    # User.Read (Graph) is incompatible with outlook.office.com scopes in v2 endpoint sometimes.
    # We only need IMAP and SMTP access.
    SCOPES = ["https://outlook.office.com/IMAP.AccessAsUser.All", "https://outlook.office.com/SMTP.Send"]
    
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
    TARGET_SENDER = os.getenv("TARGET_SENDER") # Optional: Filter by sender
    IMAP_SERVER = "outlook.office365.com"
    SMTP_SERVER = "smtp.office365.com" # Not used for drafts, but good to have
