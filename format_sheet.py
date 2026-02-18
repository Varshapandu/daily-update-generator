#!/usr/bin/env python3
"""
Utility script to format the ETA column in your Google Sheet
Run this script after pasting your Google Sheet URL
"""

from google_sheets import format_eta_column

if __name__ == "__main__":
    sheet_url = input("📋 Paste your Google Sheet URL: ").strip()
    
    if not sheet_url:
        print("❌ No URL provided")
        exit(1)
    
    try:
        print("🎨 Formatting ETA column with darker blue...")
        format_eta_column(sheet_url)
        print("✅ ETA column formatted successfully!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)
