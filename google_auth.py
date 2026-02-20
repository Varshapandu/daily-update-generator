import os
import json
import pickle

import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OAUTH_CREDENTIALS_FILE = os.path.join(BASE_DIR, "oauth_credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.pickle")
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "service_account.json")


def _get_service_account_client():
    """Try service account auth (best for hosted deployments)."""
    errors = []

    # 1) Streamlit secrets (recommended for Streamlit Cloud)
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            secret_block = st.secrets["gcp_service_account"]
            if hasattr(secret_block, "to_dict"):
                secret_block = secret_block.to_dict()
            elif not isinstance(secret_block, dict):
                secret_block = dict(secret_block)
            return gspread.service_account_from_dict(secret_block)
        errors.append("st.secrets has no [gcp_service_account] section")
    except Exception as e:
        errors.append(f"Failed reading Streamlit secrets: {e}")

    # 2) Environment variable containing JSON
    env_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if env_json:
        try:
            return gspread.service_account_from_dict(json.loads(env_json))
        except Exception as e:
            errors.append(f"Invalid GCP_SERVICE_ACCOUNT_JSON: {e}")
    else:
        errors.append("GCP_SERVICE_ACCOUNT_JSON env var not set")

    # 3) Local file (good for local dev)
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        try:
            return gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
        except Exception as e:
            errors.append(f"service_account.json exists but failed to load: {e}")
    else:
        errors.append("service_account.json not found")

    raise Exception("Service account auth failed. " + " | ".join(errors))


def get_gspread_client():
    """
    Authentication strategy:
    1) Service account (cloud-friendly)
    2) OAuth desktop flow fallback (local development)
    """
    service_account_error = None
    try:
        return _get_service_account_client()
    except Exception as e:
        service_account_error = str(e)

    creds = None

    # Load cached token if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # Refresh / create OAuth token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(OAUTH_CREDENTIALS_FILE):
                raise Exception(
                    "No Google credentials found for deployment.\n"
                    "Use one of these options:\n"
                    "1. Streamlit Cloud: add [gcp_service_account] in app Secrets\n"
                    "2. Local dev: place oauth_credentials.json in project root\n"
                    "3. Local dev: place service_account.json in project root\n\n"
                    f"Diagnostics: {service_account_error}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                OAUTH_CREDENTIALS_FILE,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return gspread.authorize(creds)
