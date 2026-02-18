# OAuth Setup Guide for Daily Update Generator

The app now uses **OAuth authentication**, which means you and your team can log in once and access any Google Sheet you have permission to edit. No more sharing requirements!

## Setup Steps (One-time only)

### 1. Create OAuth Credentials in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (if you don't have one):
   - Click "Select a Project" at the top
   - Click "NEW PROJECT"
   - Name it "Daily Update App"
   - Click "Create"

3. Enable Google Sheets API & Google Drive API:
   - Search for "Google Sheets API" → Click → Click "ENABLE"
   - Search for "Google Drive API" → Click → Click "ENABLE"

4. Create OAuth 2.0 Credentials:
   - Go to "Credentials" in the left sidebar
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application" as the type
   - Click "Create"
   - Click "Download" (or click the download icon)
   - This downloads a JSON file

5. Save the JSON file:
   - Rename it to `oauth_credentials.json`
   - Place it in: `c:\Users\varsh\OneDrive\Desktop\Daily update project\`

### 2. First Time Login

1. Open the app: `http://localhost:8501`
2. Click **"🔑 Login with Google"**
3. A browser window will pop up asking you to log in
4. Log in with your Google account
5. Click "Allow" when asked for permissions
6. The app will save your login automatically (in `token.pickle`)

### 3. Use the App

Once logged in:
1. Paste your Google Sheet URL
2. Click **"📤 Connect"**
3. Edit your tasks
4. Click **"💾 Save Today Snapshot"** to save

That's it! Your team members just need to do the same login process once.

## Important Notes

- `oauth_credentials.json` - Should be committed to git (contains no secrets)
- `token.pickle` - **DO NOT commit** (contains your auth token) - Already in `.gitignore`
- If something breaks, delete `token.pickle` and log in again
- Each user has their own `token.pickle` on their machine

## Troubleshooting

**"oauth_credentials.json not found"**
- Follow steps 1-5 above to create and download the file

**"Permission Denied"**
- Make sure you're logged in with the correct Google account
- Make sure you own or have Editor access to the Google Sheet

**"Authentication failed"**
- Delete `token.pickle` from the project folder
- Log in again using the app button
