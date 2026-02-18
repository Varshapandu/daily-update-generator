import os
import pickle
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# OAuth credentials file (get from Google Cloud Console)
OAUTH_CREDENTIALS_FILE = "oauth_credentials.json"
TOKEN_FILE = "token.pickle"


def get_gspread_client():
    """
    Authenticate using OAuth flow.
    Token is cached in token.pickle, so users only authenticate once.
    """
    creds = None
    
    # 1. Load cached token if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)
    
    # 2. If token doesn't exist or is invalid, refresh or create new
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # New authentication needed
            if not os.path.exists(OAUTH_CREDENTIALS_FILE):
                raise Exception(
                    f"OAuth credentials file '{OAUTH_CREDENTIALS_FILE}' not found.\n"
                    "Please:\n"
                    "1. Go to Google Cloud Console\n"
                    "2. Create OAuth 2.0 credentials (Desktop app)\n"
                    "3. Download JSON and save as 'oauth_credentials.json' in this folder"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                OAUTH_CREDENTIALS_FILE,
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # 3. Save token for next time
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    
    return gspread.authorize(creds)
