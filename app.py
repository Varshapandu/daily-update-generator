# import streamlit as st
# import pandas as pd

# from google_sheets import load_google_sheet_by_id
# from exporter import export_to_excel, export_to_csv

# # --------------------------------------------------
# # Page configuration
# # --------------------------------------------------
# st.set_page_config(
#     page_title="Daily Update Generator",
#     layout="wide"
# )

# st.title("📊 Daily Update Generator")

# st.markdown(
#     """
#     **Flow**
#     1. Attach Google Sheet / Excel / CSV  
#     2. Edit or add rows / columns  
#     3. Download daily update
#     """
# )

# # --------------------------------------------------
# # Initialize session state (EFFICIENCY CORE)
# # --------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None

# if "sheet_id" not in st.session_state:
#     st.session_state.sheet_id = None

# if "source_type" not in st.session_state:
#     st.session_state.source_type = None


# # --------------------------------------------------
# # Attach data source
# # --------------------------------------------------
# st.subheader("📎 Attach Data Source")

# uploaded_file = st.file_uploader(
#     "Upload Excel or CSV file",
#     type=["xlsx", "csv"]
# )

# sheet_url = st.text_input(
#     "OR paste Google Sheet URL",
#     placeholder="https://docs.google.com/spreadsheets/d/..."
# )

# if st.button("Attach Source"):

#     # ---------- Excel / CSV ----------
#     if uploaded_file is not None:
#         try:
#             if uploaded_file.name.endswith(".csv"):
#                 df = pd.read_csv(uploaded_file)
#             else:
#                 df = pd.read_excel(uploaded_file)

#             st.session_state.df = df
#             st.session_state.sheet_id = None
#             st.session_state.source_type = "file"

#             st.success("File attached successfully ✅")

#         except Exception as e:
#             st.error("Failed to read file")
#             st.exception(e)

#     # ---------- Google Sheet ----------
#     elif sheet_url:
#         try:
#             # Extract Sheet ID automatically
#             sheet_id = sheet_url.split("/d/")[1].split("/")[0]

#             df = load_google_sheet_by_id(sheet_id)

#             st.session_state.df = df
#             st.session_state.sheet_id = sheet_id
#             st.session_state.source_type = "google_sheet"

#             st.success("Google Sheet attached successfully ✅")

#         except Exception as e:
#             st.error("Failed to load Google Sheet")
#             st.exception(e)

#     else:
#         st.warning("Please upload a file or paste a Google Sheet URL")


# # --------------------------------------------------
# # Editable table (NO API CALLS HERE)
# # --------------------------------------------------
# if st.session_state.df is not None:

#     st.subheader("✍️ Editable Daily Update Table")

#     edited_df = st.data_editor(
#         st.session_state.df,
#         num_rows="dynamic",
#         use_container_width=True
#     )

#     # Update working copy in memory
#     st.session_state.df = edited_df


#     # --------------------------------------------------
#     # Refresh (ONLY for Google Sheets)
#     # --------------------------------------------------
#     if st.session_state.source_type == "google_sheet":
#         if st.button("🔄 Refresh from Google Sheet"):
#             try:
#                 refreshed_df = load_google_sheet_by_id(
#                     st.session_state.sheet_id
#                 )
#                 st.session_state.df = refreshed_df
#                 st.success("Sheet refreshed successfully")
#             except Exception as e:
#                 st.error("Failed to refresh sheet")
#                 st.exception(e)


#     # --------------------------------------------------
#     # Downloads
#     # --------------------------------------------------
#     st.subheader("⬇️ Download Daily Update")

#     excel_bytes = export_to_excel(st.session_state.df)
#     csv_bytes = export_to_csv(st.session_state.df)

#     col1, col2 = st.columns(2)

#     with col1:
#         st.download_button(
#             "⬇️ Download Excel",
#             data=excel_bytes,
#             file_name="Daily_Update.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )

#     with col2:
#         st.download_button(
#             "⬇️ Download CSV",
#             data=csv_bytes,
#             file_name="Daily_Update.csv",
#             mime="text/csv"
#         )

# #2
# import streamlit as st
# import pandas as pd
# import warnings
# from exporter import export_to_excel, export_to_csv

# # --------------------------------------------------
# # Silence Streamlit/Pandas internal warning
# # --------------------------------------------------
# warnings.filterwarnings(
#     "ignore",
#     category=FutureWarning,
# )

# # --------------------------------------------------
# # Page config
# # --------------------------------------------------
# st.set_page_config(page_title="Daily Update Generator", layout="wide")
# st.title("📊 Daily Update Generator")

# st.markdown(
#     """
#     **Flow**
#     1. Upload Excel / CSV  
#     2. Edit or add rows / columns  
#     3. Download daily update
#     """
# )

# # --------------------------------------------------
# # Status config
# # --------------------------------------------------
# STATUS_OPTIONS = [
#     "🟡 In Progress",
#     "🟢 Completed",
#     "🔴 At Risk",
#     "⚫ Blocked",
# ]

# STATUS_NORMALIZE = {
#     "In Progress": "🟡 In Progress",
#     "Completed": "🟢 Completed",
#     "At Risk": "🔴 At Risk",
#     "Blocked": "⚫ Blocked",
#     "🟡 In Progress": "🟡 In Progress",
#     "🟢 Completed": "🟢 Completed",
#     "🔴 At Risk": "🔴 At Risk",
#     "⚫ Blocked": "⚫ Blocked",
# }

# # --------------------------------------------------
# # HARD NORMALIZER (THIS FIXES EVERYTHING)
# # --------------------------------------------------
# def normalize_df_for_streamlit(df: pd.DataFrame) -> pd.DataFrame:
#     df = df.copy()

#     # 1️⃣ Fix column names (NO NaN ALLOWED)
#     df.columns = [str(c).strip() if pd.notna(c) else "" for c in df.columns]

#     # 2️⃣ Reset index (Arrow-safe)
#     df = df.reset_index(drop=True)

#     # 3️⃣ Convert datetimes explicitly
#     if "ETA / Follow-up" in df.columns:
#         df["ETA / Follow-up"] = pd.to_datetime(
#             df["ETA / Follow-up"], errors="coerce"
#         )

#     # 4️⃣ Normalize status
#     if "Status" in df.columns:
#         df["Status"] = (
#             df["Status"]
#             .astype(str)
#             .map(lambda x: STATUS_NORMALIZE.get(x, "🟡 In Progress"))
#         )

#     # 5️⃣ Kill NaN everywhere (JSON-safe)
#     for col in df.columns:
#         if col == "ETA / Follow-up":
#             df[col] = df[col].where(df[col].notna(), None)
#         elif col == "Status":
#             df[col] = df[col].fillna("🟡 In Progress")
#         else:
#             df[col] = df[col].fillna("")

#     # 6️⃣ Force plain Python objects (NO pandas NA / Arrow tricks)
#     df = df.astype(object)

#     return df


# # --------------------------------------------------
# # Load file & fix headers
# # --------------------------------------------------
# def load_file(uploaded_file) -> pd.DataFrame:
#     if uploaded_file.name.endswith(".csv"):
#         raw = pd.read_csv(uploaded_file, header=None)
#     else:
#         raw = pd.read_excel(uploaded_file, header=None)

#     # Find header row containing "Action Item"
#     header_row = raw[
#         raw.apply(
#             lambda r: r.astype(str)
#             .str.contains("Action Item", case=False, na=False)
#             .any(),
#             axis=1,
#         )
#     ].index[0]

#     df = raw.iloc[header_row + 1 :].copy()
#     df.columns = raw.iloc[header_row]
#     df = df.reset_index(drop=True)

#     return df


# # --------------------------------------------------
# # Session state
# # --------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None


# # --------------------------------------------------
# # Upload
# # --------------------------------------------------
# st.subheader("📎 Upload Data File")

# uploaded_file = st.file_uploader(
#     "Upload Excel or CSV",
#     type=["xlsx", "csv"],
# )

# if uploaded_file:
#     try:
#         df = load_file(uploaded_file)
#         df = normalize_df_for_streamlit(df)
#         st.session_state.df = df
#         st.success("File loaded successfully ✅")
#     except Exception as e:
#         st.error("Failed to load file")
#         st.exception(e)


# # --------------------------------------------------
# # Editor
# # --------------------------------------------------
# if st.session_state.df is not None:

#     st.subheader("✍️ Editable Daily Update Table")

#     edited_df = st.data_editor(
#         st.session_state.df,
#         num_rows="dynamic",
#         width="stretch",
#         column_config={
#             "ETA / Follow-up": st.column_config.DatetimeColumn(
#                 "ETA / Follow-up",
#                 format="YYYY-MM-DD HH:mm",
#                 step=60,
#             ),
#             "Status": st.column_config.SelectboxColumn(
#                 "Status",
#                 options=STATUS_OPTIONS,
#             ),
#         },
#     )

#     edited_df = normalize_df_for_streamlit(edited_df)
#     st.session_state.df = edited_df

#     # --------------------------------------------------
#     # Downloads
#     # --------------------------------------------------
#     st.subheader("⬇️ Download Daily Update")

#     col1, col2 = st.columns(2)

#     with col1:
#         st.download_button(
#             "⬇️ Download Excel",
#             export_to_excel(edited_df),
#             "Daily_Update.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )

#     with col2:
#         st.download_button(
#             "⬇️ Download CSV",
#             export_to_csv(edited_df),
#             "Daily_Update.csv",
#             mime="text/csv",
#         )

# import streamlit as st
# import pandas as pd
# import warnings

# from exporter import export_to_excel, export_to_csv
# from google_sheets import load_sheet, save_sheet

# # --------------------------------------------------
# # Silence internal warnings (safe)
# # --------------------------------------------------
# warnings.filterwarnings("ignore", category=FutureWarning)

# # --------------------------------------------------
# # Page config
# # --------------------------------------------------
# st.set_page_config(page_title="Daily Update Generator", layout="wide")
# st.title("📊 Daily Update Generator")

# st.markdown(
#     """
# **Flow**
# 1. Connect Google Sheet **or** Upload Excel/CSV **or** Create table  
# 2. Edit together (shared)  
# 3. Save to Google Sheet / Download
# """
# )

# # --------------------------------------------------
# # Status config
# # --------------------------------------------------
# STATUS_OPTIONS = [
#     "🟡 In Progress",
#     "🟢 Completed",
#     "🔴 At Risk",
#     "⚫ Blocked",
# ]

# STATUS_NORMALIZE = {
#     "In Progress": "🟡 In Progress",
#     "Completed": "🟢 Completed",
#     "At Risk": "🔴 At Risk",
#     "Blocked": "⚫ Blocked",
#     "🟡 In Progress": "🟡 In Progress",
#     "🟢 Completed": "🟢 Completed",
#     "🔴 At Risk": "🔴 At Risk",
#     "⚫ Blocked": "⚫ Blocked",
# }

# # --------------------------------------------------
# # Helpers (CRITICAL for stability)
# # --------------------------------------------------
# def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
#     df = df.copy()

#     # Clean column names
#     df.columns = [str(c).strip() for c in df.columns]

#     # ETA column → datetime (allow None)
#     if "ETA / Follow-up" in df.columns:
#         df["ETA / Follow-up"] = pd.to_datetime(
#             df["ETA / Follow-up"], errors="coerce"
#         )

#     # Status normalization
#     if "Status" in df.columns:
#         df["Status"] = (
#             df["Status"]
#             .astype(str)
#             .map(lambda x: STATUS_NORMALIZE.get(x, "🟡 In Progress"))
#         )

#     # Replace NaN with safe values (VERY IMPORTANT)
#     for col in df.columns:
#         if col == "ETA / Follow-up":
#             df[col] = df[col].where(df[col].notna(), None)
#         elif col == "Status":
#             df[col] = df[col].fillna("🟡 In Progress")
#         else:
#             df[col] = df[col].fillna("")

#     return df.astype(object)


# def create_empty_table() -> pd.DataFrame:
#     return normalize_df(
#         pd.DataFrame(
#             {
#                 "Action Item": [""],
#                 "Owner": [""],
#                 "ETA / Follow-up": [None],
#                 "Status": ["🟡 In Progress"],
#                 "Notes / Completion Callout": [""],
#             }
#         )
#     )


# def load_uploaded_file(uploaded_file) -> pd.DataFrame:
#     if uploaded_file.name.endswith(".csv"):
#         df = pd.read_csv(uploaded_file)
#     else:
#         df = pd.read_excel(uploaded_file)

#     return normalize_df(df)


# # --------------------------------------------------
# # Session state
# # --------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None

# if "sheet_url" not in st.session_state:
#     st.session_state.sheet_url = None

# # --------------------------------------------------
# # Google Sheet (shared for team)
# # --------------------------------------------------
# st.subheader("🔗 Connect Shared Google Sheet")

# sheet_url = st.text_input(
#     "Paste Google Sheet URL",
#     placeholder="https://docs.google.com/spreadsheets/d/..."
# )

# if st.button("Connect Google Sheet"):
#     try:
#         df = load_sheet(sheet_url)
#         st.session_state.df = normalize_df(df)
#         st.session_state.sheet_url = sheet_url
#         st.success("Google Sheet connected ✅ (shared for team)")
#     except Exception as e:
#         st.error("Failed to load Google Sheet")
#         st.exception(e)

# # --------------------------------------------------
# # Upload Excel / CSV
# # --------------------------------------------------
# st.markdown("---")
# st.subheader("📎 Upload Excel / CSV")

# uploaded_file = st.file_uploader(
#     "Upload file",
#     type=["xlsx", "csv"]
# )

# if uploaded_file:
#     try:
#         st.session_state.df = load_uploaded_file(uploaded_file)
#         st.session_state.sheet_url = None
#         st.success("File loaded successfully ✅")
#     except Exception as e:
#         st.error("Failed to load file")
#         st.exception(e)

# # --------------------------------------------------
# # Create from scratch
# # --------------------------------------------------
# st.markdown("---")
# st.subheader("🆕 Create Table from Scratch")

# if st.button("➕ Create Empty Daily Update Table"):
#     st.session_state.df = create_empty_table()
#     st.session_state.sheet_url = None
#     st.success("Empty daily update table created ✅")

# # --------------------------------------------------
# # Editable table
# # --------------------------------------------------
# if st.session_state.df is not None:

#     st.subheader("✍️ Editable Daily Update Table")

#     edited_df = st.data_editor(
#         st.session_state.df,
#         num_rows="dynamic",
#         width="stretch",
#         column_config={
#             "ETA / Follow-up": st.column_config.DatetimeColumn(
#                 "ETA / Follow-up",
#                 format="YYYY-MM-DD HH:mm",
#                 step=60,
#             ),
#             "Status": st.column_config.SelectboxColumn(
#                 "Status",
#                 options=STATUS_OPTIONS,
#             ),
#         },
#     )

#     edited_df = normalize_df(edited_df)
#     st.session_state.df = edited_df

#     # --------------------------------------------------
#     # Save back to Google Sheet
#     # --------------------------------------------------
#     if st.session_state.sheet_url:
#         if st.button("💾 Save to Google Sheet"):
#             save_sheet(st.session_state.sheet_url, edited_df)
#             st.success("Saved to Google Sheet ✅ (team updated)")

#     # --------------------------------------------------
#     # Downloads
#     # --------------------------------------------------
#     st.markdown("---")
#     st.subheader("⬇️ Download Daily Update")

#     col1, col2 = st.columns(2)

#     with col1:
#         st.download_button(
#             "⬇️ Download Excel",
#             export_to_excel(edited_df),
#             "Daily_Update.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         )

#     with col2:
#         st.download_button(
#             "⬇️ Download CSV",
#             export_to_csv(edited_df),
#             "Daily_Update.csv",
#             mime="text/csv",
#         )

import streamlit as st
import pandas as pd
from datetime import datetime
from google_auth import get_gspread_client

# ==========================================================
# CONFIG & STYLING
# ==========================================================

st.set_page_config(page_title="Daily Update Generator", layout="wide")

# Professional CSS styling
st.markdown("""
    <style>
        /* ============================================
           DESIGN TOKENS & VARIABLES
           ============================================ */
        :root {
            /* Color Palette - Soft Pastel */
            --color-primary: #A78BFA;
            --color-primary-light: #F3E8FF;
            --color-primary-dark: #7C3AED;
            --color-secondary: #C4B5FD;
            --color-success: #86EFAC;
            --color-success-light: #DCFCE7;
            --color-warning: #FCD34D;
            --color-warning-light: #FEF9E7;
            --color-danger: #FCA5A5;
            --color-danger-light: #FEE2E2;
            --color-info: #A5F3FC;
            --color-info-light: #ECFDF5;
            
            /* Neutral Palette */
            --color-white: #FFFFFF;
            --color-gray-50: #FFFBF0;
            --color-gray-100: #FAF8F3;
            --color-gray-200: #F3F1EB;
            --color-gray-300: #E8E3D8;
            --color-gray-400: #D4CCC0;
            --color-gray-500: #B8AFA0;
            --color-gray-600: #8B8680;
            --color-gray-700: #5F5952;
            --color-gray-800: #3F3936;
            --color-gray-900: #2A2724;
            
            /* Semantic Colors */
            --bg-primary: linear-gradient(135deg, #C7D2FE 0%, #DDD6FE 100%);
            --bg-secondary: linear-gradient(135deg, #FBCFE8 0%, #FECACA 100%);
            --bg-surface: #FFFFFF;
            --bg-surface-alt: #FFFBF0;
            --bg-overlay: rgba(0, 0, 0, 0.5);
            
            /* Typography */
            --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            --font-size-xs: 0.75rem;
            --font-size-sm: 0.875rem;
            --font-size-base: 1rem;
            --font-size-lg: 1.125rem;
            --font-size-xl: 1.25rem;
            --font-size-2xl: 1.5rem;
            --font-size-3xl: 1.875rem;
            --font-line-height-tight: 1.25;
            --font-line-height-normal: 1.5;
            --font-line-height-relaxed: 1.75;
            --font-weight-regular: 400;
            --font-weight-medium: 500;
            --font-weight-semibold: 600;
            --font-weight-bold: 700;
            
            /* Spacing System (8px base) */
            --spacing-0: 0;
            --spacing-1: 0.25rem;
            --spacing-2: 0.5rem;
            --spacing-3: 0.75rem;
            --spacing-4: 1rem;
            --spacing-6: 1.5rem;
            --spacing-8: 2rem;
            --spacing-10: 2.5rem;
            --spacing-12: 3rem;
            --spacing-16: 4rem;
            --spacing-20: 5rem;
            --spacing-24: 6rem;
            
            /* Border Radius */
            --radius-sm: 0.375rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            --radius-2xl: 1.5rem;
            
            /* Shadows */
            --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px 0 rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.03);
            
            /* Transitions */
            --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* ============================================
           GLOBAL STYLES
           ============================================ */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            font-family: var(--font-family-base);
            font-size: var(--font-size-base);
            line-height: var(--font-line-height-normal);
            color: var(--color-gray-900);
        }
        
        .stApp {
            background-color: var(--color-gray-50);
        }
        
        /* Ensure all text elements are visible */
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stMarkdownContainer"] h6 {
            color: #5F5952 !important;
            font-weight: 700 !important;
        }
        
        /* ============================================
           TYPOGRAPHY
           ============================================ */
        h1, h2, h3, h4, h5, h6 {
            font-weight: var(--font-weight-bold);
            line-height: var(--font-line-height-tight);
            color: #5F5952;
            margin-top: var(--spacing-8);
        }
        
        h1 {
            font-size: var(--font-size-3xl);
            margin-bottom: var(--spacing-8);
            color: #5F5952;
        }
        
        h2 {
            font-size: var(--font-size-2xl);
            margin-bottom: var(--spacing-6);
            color: #5F5952;
        }
        
        h3 {
            font-size: var(--font-size-xl);
            margin-bottom: var(--spacing-4);
            color: #5F5952;
            font-weight: 700;
        }
        
        h4, h5, h6 {
            font-size: var(--font-size-lg);
            color: #5F5952;
        }
        
        p {
            margin-bottom: var(--spacing-4);
            color: var(--color-gray-700);
        }
        
        a {
            color: var(--color-primary);
            text-decoration: none;
            transition: color var(--transition-base);
        }
        
        a:hover {
            color: var(--color-primary-dark);
            text-decoration: underline;
        }
        
        /* ============================================
           BUTTONS
           ============================================ */
        .stButton > button,
        [data-testid="stDownloadButton"] > button {
            background: #D4E9F7 !important;
            color: #1B5E7E !important;
            border: 1px solid #A5D3E8 !important;
            border-radius: var(--radius-lg) !important;
            padding: var(--spacing-3) var(--spacing-6) !important;
            font-size: var(--font-size-base) !important;
            font-weight: var(--font-weight-semibold) !important;
            cursor: pointer !important;
            transition: all var(--transition-base) !important;
            box-shadow: var(--shadow-sm) !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: var(--spacing-2) !important;
            width: 100% !important;
        }
        
        .stButton > button:hover,
        [data-testid="stDownloadButton"] > button:hover {
            background: #B5D9E8 !important;
            box-shadow: var(--shadow-lg) !important;
            transform: translateY(-1px) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0);
            box-shadow: var(--shadow-md);
        }
        
        .stButton > button:focus {
            outline: 2px solid transparent;
            outline-offset: 2px;
            box-shadow: 0 0 0 3px var(--color-primary-light);
        }
        
        .stButton > button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* ============================================
           INPUTS & FORMS
           ============================================ */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"] {
            border-radius: var(--radius-lg);
            border: 1px solid var(--color-gray-300);
            padding: var(--spacing-2) var(--spacing-4);
            font-size: var(--font-size-base);
            transition: all var(--transition-base);
            background-color: var(--color-white);
            color: var(--color-gray-900);
        }
        
        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stSelectbox [data-baseweb="select"]:focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px var(--color-primary-light);
            outline: none;
        }
        
        .stTextInput input::placeholder {
            color: var(--color-gray-400);
        }
        
        /* Multiselect container - light grey background */
        [data-baseweb="base-select"],
        [data-baseweb="popover"],
        .stMultiSelect [data-baseweb="base-select"] {
            background-color: #FAF8F3 !important;
        }
        
        /* Multiselect search input */
        [data-baseweb="input"] {
            background-color: #FAF8F3 !important;
            color: #5F5952 !important;
        }
        
        /* Multiselect container background */
        div[data-baseweb="select"] {
            background-color: #FAF8F3 !important;
        }
        
        /* Multiselect wrapper - light background */
        [class*="stMultiSelect"] {
            background-color: #FAF8F3 !important;
        }
        
        /* Multiselect input container */
        [data-baseweb="select"] > div {
            background-color: #FAF8F3 !important;
        }
        
        /* All text inside multiselect - dark and readable */
        [data-baseweb="tag"] {
            background-color: #C7D2FE !important;
            color: #5F5952 !important;
            border-radius: 6px !important;
        }
        
        [data-baseweb="tag"] > span {
            color: #5F5952 !important;
        }
        
        /* Text labels and option text inside selects */
        [data-baseweb="select"] span,
        [data-baseweb="base-select"] span,
        [data-baseweb="base-select"] div {
            color: #5F5952 !important;
        }
        
        /* Option items text */
        [role="option"] {
            color: #5F5952 !important;
        }
        
        [role="option"]:hover {
            background-color: #E8E3D8 !important;
        }
        
        /* ============================================
           CARDS & CONTAINERS
           ============================================ */
        .metric-card,
        [data-testid="stMetricDelta"],
        [data-testid="stMetricValue"] {
            background: var(--color-white);
            border-radius: var(--radius-xl);
            border: 1px solid var(--color-gray-200);
            padding: var(--spacing-6);
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-base);
        }
        
        .metric-card:hover {
            box-shadow: var(--shadow-md);
            border-color: var(--color-gray-300);
        }
        
        /* ============================================
           DATA EDITOR & TABLES
           ============================================ */
        .stDataFrame,
        [data-testid="stDataFrame"] {
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }
        
        .stDataFrame table,
        [data-testid="stDataFrame"] table {
            border-collapse: collapse;
            width: 100%;
        }
        
        .stDataFrame th,
        [data-testid="stDataFrame"] th {
            background-color: var(--color-gray-100);
            color: var(--color-gray-900);
            font-weight: var(--font-weight-semibold);
            padding: var(--spacing-3) var(--spacing-4);
            text-align: left;
            border-bottom: 2px solid var(--color-gray-300);
        }
        
        .stDataFrame td,
        [data-testid="stDataFrame"] td {
            padding: var(--spacing-3) var(--spacing-4);
            border-bottom: 1px solid var(--color-gray-200);
            color: var(--color-gray-700);
        }
        
        /* ETA / Date columns - darker and more prominent */
        .stDataFrame td:nth-child(4),
        [data-testid="stDataFrame"] td:nth-child(4) {
            color: #3F3936 !important;
            font-weight: 600 !important;
            background-color: #FFFBF0 !important;
        }
        
        .stDataFrame tr:hover,
        [data-testid="stDataFrame"] tr:hover {
            background-color: var(--color-gray-50);
        }
        
        /* ============================================
           ALERTS & MESSAGES
           ============================================ */
        [data-testid="stAlert"] {
            border-radius: var(--radius-lg);
            border-left: 4px solid;
            padding: var(--spacing-4);
            margin-bottom: var(--spacing-4);
        }
        
        [data-testid="stAlert"][kind="success"] {
            background-color: #DCFCE7;
            border-left-color: #86EFAC;
            color: #166534;
        }
        
        [data-testid="stAlert"][kind="warning"] {
            background-color: #FEF9E7;
            border-left-color: #FCD34D;
            color: #78350F;
        }
        
        [data-testid="stAlert"][kind="error"] {
            background-color: #FEE2E2;
            border-left-color: #FCA5A5;
            color: #7F1D1D;
        }
        
        [data-testid="stAlert"][kind="info"] {
            background-color: #ECFDF5;
            border-left-color: #A5F3FC;
            color: #164E63;
        }
        
        /* ============================================
           DATE PICKER
           ============================================ */
        /* Date picker input */
        input[type="date"],
        [data-baseweb="datepicker"] input {
            background-color: #FFFFFF !important;
            color: #5F5952 !important;
            border: 1px solid #D4CCC0 !important;
            border-radius: var(--radius-lg) !important;
            padding: var(--spacing-2) var(--spacing-4) !important;
        }
        
        /* Calendar popup wrapper */
        [data-baseweb="datepicker"] {
            background-color: #FAF8F3 !important;
        }
        
        /* Popover (calendar container) */
        [data-baseweb="popover"],
        div[role="dialog"],
        [class*="Popover"] {
            background-color: #FAF8F3 !important;
        }
        
        /* Calendar root */
        [class*="Calendar"],
        [class*="react-day-picker"],
        .DayPicker {
            background-color: #FAF8F3 !important;
            color: #5F5952 !important;
        }
        
        /* Calendar wrapper div */
        [data-baseweb="datepicker"] div,
        [class*="Calendar__Root"] {
            background-color: #FAF8F3 !important;
            color: #5F5952 !important;
        }
        
        /* Header (month/year) */
        [class*="Calendar__Header"],
        [class*="Header"],
        thead {
            background-color: #E8E3D8 !important;
            color: #5F5952 !important;
        }
        
        /* Month/Year text */
        [class*="Calendar__Title"],
        [class*="Title"] {
            color: #5F5952 !important;
        }
        
        /* Calendar body */
        [class*="Calendar__Body"],
        tbody {
            background-color: #FAF8F3 !important;
        }
        
        /* Day cells */
        [class*="Day"],
        [class*="day"],
        td button,
        td div,
        button[class*="Day"] {
            background-color: #FFFFFF !important;
            color: #5F5952 !important;
            border: 1px solid #F3E8FF !important;
        }
        
        /* Day hover */
        [class*="Day"]:hover,
        td button:hover,
        button[class*="Day"]:hover {
            background-color: #E8E3D8 !important;
            color: #5F5952 !important;
        }
        
        /* Selected date */
        [class*="Day"][class*="selected"],
        [class*="Day"][class*="highlighted"],
        [class*="Day"][aria-selected="true"],
        button[class*="Day"][aria-selected="true"],
        td button[aria-selected="true"] {
            background-color: #A78BFA !important;
            color: #FFFFFF !important;
            border-color: #A78BFA !important;
        }
        
        /* Disabled days */
        [class*="Day"][disabled],
        button[class*="Day"][disabled] {
            background-color: #F3E8FF !important;
            color: #D4CCC0 !important;
            opacity: 0.5 !important;
            cursor: not-allowed !important;
        }
        
        /* Weekday headers */
        th {
            background-color: #E8E3D8 !important;
            color: #8B8680 !important;
            font-weight: 600 !important;
            padding: 8px !important;
        }
        
        /* Today indicator */
        [class*="Today"] {
            border: 2px solid #A78BFA !important;
        }
        
        /* Navigation buttons */
        button[aria-label*="previous"],
        button[aria-label*="next"],
        [class*="Navigation"] button {
            background-color: #E8E3D8 !important;
            color: #5F5952 !important;
            border: 1px solid #D4CCC0 !important;
            border-radius: var(--radius-md) !important;
        }
        
        button[aria-label*="previous"]:hover,
        button[aria-label*="next"]:hover,
        [class*="Navigation"] button:hover {
            background-color: #D4CCC0 !important;
        }
        
        /* Ensure all elements inside calendar are visible */
        [data-baseweb="datepicker"] * {
            background-color: inherit !important;
            color: #5F5952 !important;
        }
        
        /* Date styling - darker and more prominent */
        /* Timeline and card dates */
        .date-label,
        [class*="date"],
        span:has(+ *):contains("/") {
            color: #2A2724 !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
        }
        
        /* All date text in metrics and cards */
        [data-testid="stMetric"] div,
        .metric-card span {
            /* Inherited styles for dates */
        }
        
        hr {
            border: none;
            height: 1px;
            background: var(--color-gray-200);
            margin: var(--spacing-6) 0;
        }
        
        /* ============================================
           LAYOUT & SPACING
           ============================================ */
        [data-testid="column"] {
            display: flex !important;
            align-items: center !important;
        }
        
        /* Column container alignment */
        .stColumns,
        [data-testid="stColumns"] {
            gap: 1rem !important;
            align-items: stretch !important;
        }
        [data-testid="stSidebar"] {
            background-color: var(--color-white);
            border-right: 1px solid var(--color-gray-200);
        }
        
        /* ============================================
           COLUMNS
           ============================================ */
        [data-testid="column"] {
            gap: var(--spacing-6);
        }
        
        /* ============================================
           RESPONSIVE
           ============================================ */
        @media (max-width: 768px) {
            h1 {
                font-size: var(--font-size-2xl);
                margin-bottom: var(--spacing-6);
            }
            
            h2 {
                font-size: var(--font-size-xl);
                margin-bottom: var(--spacing-4);
            }
            
            .metric-card {
                padding: var(--spacing-4);
            }
        }
        
        /* ============================================
           CALENDAR HARDFIX (AGGRESSIVE OVERRIDE)
           ============================================ */
        /* Entire calendar dropdown */
        [role="dialog"],
        [data-testid="stDateInput"] [role="dialog"],
        .calendar-popup {
            background: linear-gradient(135deg, #FFFBF0, #FAF8F3) !important;
            border: 2px solid #D4CCC0 !important;
        }
        
        /* Everything in calendar */
        [role="dialog"] * {
            background-color: transparent !important;
        }
        
        /* Calendar main container with dark background */
        div[style*="background"] {
            background-color: #FAF8F3 !important;
            color: #5F5952 !important;
        }
        
        /* Specifically target dark containers */
        div[style*="rgb(45, 45, 45)"],
        div[style*="rgb(29, 29, 29)"],
        div[style*="#2d2d2d"],
        div[style*="#1d1d1d"] {
            background-color: #FAF8F3 !important;
            color: #5F5952 !important;
        }
        
        /* All buttons in calendar */
        [role="dialog"] button {
            background-color: #FFFFFF !important;
            color: #5F5952 !important;
            border: 1px solid #D4CCC0 !important;
            padding: 8px 12px !important;
            border-radius: 6px !important;
        }
        
        [role="dialog"] button:hover,
        [role="dialog"] button:focus {
            background-color: #E8E3D8 !important;
            border-color: #A78BFA !important;
        }
        
        /* Selected button */
        [role="dialog"] button[aria-selected="true"],
        [role="dialog"] button:selected {
            background-color: #A78BFA !important;
            color: #FFFFFF !important;
            border-color: #A78BFA !important;
            font-weight: 600 !important;
        }
        
        /* Month/Year header text */
        [role="dialog"] h2,
        [role="dialog"] [role="heading"] {
            color: #5F5952 !important;
            background-color: transparent !important;
        }
        
        /* All spans and text */
        [role="dialog"] span {
            color: #5F5952 !important;
        }
        
        /* ============================================
           ACCESSIBILITY
           ============================================ */
        *:focus-visible {
            outline: 2px solid var(--color-primary);
            outline-offset: 2px;
        }
        
        @media (prefers-reduced-motion: reduce) {
            * {
                transition: none !important;
                animation: none !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Daily Update Generator")

# Add intro section
st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(199, 210, 254, 0.4) 0%, rgba(221, 214, 254, 0.4) 100%);
        border-left: 4px solid #A78BFA;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 32px;
        border: 1px solid rgba(199, 210, 254, 0.6);
    ">
        <h3 style="margin-top: 0; color: #5F5952; font-size: 18px; font-weight: 600;">✨ Welcome to Your Daily Update Dashboard</h3>
        <p style="color: #8B8680; margin: 12px 0; font-size: 15px; line-height: 1.6;">
            <span style="font-weight: 500;">🔗 Connect</span> your Google Sheet → 
            <span style="font-weight: 500;">✏️ Edit</span> your tasks → 
            <span style="font-weight: 500;">💾 Save</span> snapshots → 
            <span style="font-weight: 500;">📊 Visualize</span> your timeline
        </p>
        <p style="color: #A8A0A0; margin: 0; font-size: 14px; line-height: 1.5;">
            Keep your team aligned with real-time task tracking and status updates.
        </p>
    </div>
""", unsafe_allow_html=True)

CONSTANT_COLUMNS = [
    "Snapshot Date",
    "Category",
    "Client / Partner",
    "Action Item",
    "Owner",
    "ETA / Follow-up",
    "Status",
    "Notes / Completion Callout"
]

STATUS_OPTIONS = [
    "🟡 In Progress",
    "🔴 At Risk",
    "⚫ Closed",
    "🟢 Ongoing"
]

# ==========================================================
# SMART DATE CLEANER
# ==========================================================

def clean_eta_column(series):
    current_year = datetime.today().year
    cleaned = []

    for val in series:
        if not val or str(val).strip() in ["—", "None", "nan"]:
            cleaned.append(pd.NaT)
            continue

        val = str(val).strip()

        # Handle 28-Jan format
        if "-" in val and len(val) <= 6:
            val = f"{val}-{current_year}"

        try:
            parsed = pd.to_datetime(val, format="%d-%b-%Y", errors="coerce")
            if pd.isna(parsed):
                parsed = pd.to_datetime(val, errors="coerce")
        except:
            parsed = pd.NaT

        cleaned.append(parsed)

    return pd.Series(cleaned)

# # ==========================================================
# # LOAD GOOGLE SHEET (AUTO HEADER DETECTION)
# # ==========================================================

# def load_master_sheet(sheet_url):
#     gc = get_gspread_client()
#     sh = gc.open_by_url(sheet_url)
#     ws = sh.sheet1

#     values = ws.get_all_values()

#     if not values:
#         return pd.DataFrame(columns=CONSTANT_COLUMNS)

#     # 🔍 Detect header row (row containing "Action Item")
#     header_index = None
#     for i, row in enumerate(values[:20]):
#         if "Action Item" in row:
#             header_index = i
#             break

#     if header_index is None:
#         st.error("Could not detect header row.")
#         return pd.DataFrame(columns=CONSTANT_COLUMNS)

#     headers = values[header_index]
#     data = values[header_index + 1:]

#     df = pd.DataFrame(data, columns=headers)

#     # Ensure constant columns exist
#     for col in CONSTANT_COLUMNS:
#         if col not in df.columns:
#             df[col] = ""

#     df = df[CONSTANT_COLUMNS]

#     # Clean Dates
#     df["Snapshot Date"] = pd.to_datetime(
#         df["Snapshot Date"], errors="coerce", dayfirst=True
#     )

#     df["ETA / Follow-up"] = clean_eta_column(df["ETA / Follow-up"])

#     # Clean Status
#     df["Status"] = df["Status"].replace({
#         "In Progress": "🟡 In Progress",
#         "At Risk": "🔴 At Risk",
#         "Closed": "⚫ Closed",
#         "Ongoing": "🟢 Ongoing"
#     })

#     return df
# def load_master_sheet(sheet_url):
#     print("\n================= LOAD MASTER SHEET START =================")

#     gc = get_gspread_client()
#     sh = gc.open_by_url(sheet_url)
#     ws = sh.sheet1

#     values = ws.get_all_values()

#     print("RAW FIRST 5 ROWS FROM GOOGLE:")
#     for row in values[:5]:
#         print(row)

#     if not values:
#         print("Sheet is empty.")
#         return pd.DataFrame(columns=CONSTANT_COLUMNS)

#     # 🔍 Detect header row
#     header_index = None
#     for i, row in enumerate(values[:20]):
#         if "Action Item" in row:
#             header_index = i
#             break

#     print("Detected header_index:", header_index)

#     if header_index is None:
#         print("Header not detected!")
#         st.error("Could not detect header row.")
#         return pd.DataFrame(columns=CONSTANT_COLUMNS)

#     headers = values[header_index]
#     print("HEADERS DETECTED:", headers)

#     data = values[header_index + 1:]

#     df = pd.DataFrame(data, columns=headers)

#     print("\nDATAFRAME HEAD BEFORE COLUMN CLEAN:")
#     print(df.head())

#     # Ensure constant columns exist
#     for col in CONSTANT_COLUMNS:
#         if col not in df.columns:
#             print("Missing column detected:", col)
#             df[col] = ""

#     df = df[CONSTANT_COLUMNS]

#     print("\nSNAPSHOT DATE BEFORE PARSE:")
#     print(df["Snapshot Date"].head())

#     # Clean Dates
#     df["Snapshot Date"] = pd.to_datetime(
#         df["Snapshot Date"], errors="coerce", dayfirst=True
#     )

#     print("\nSNAPSHOT DATE AFTER PARSE:")
#     print(df["Snapshot Date"].head())

#     print("\nETA BEFORE CLEAN:")
#     print(df["ETA / Follow-up"].head())

#     df["ETA / Follow-up"] = clean_eta_column(df["ETA / Follow-up"])

#     print("\nETA AFTER CLEAN:")
#     print(df["ETA / Follow-up"].head())

#     print("================= LOAD MASTER SHEET END =================\n")

#     return df
def load_master_sheet(sheet_url):
    gc = get_gspread_client()
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1

    values = ws.get_all_values()

    if not values:
        return pd.DataFrame(columns=CONSTANT_COLUMNS)

    # Detect header row
    header_index = None
    for i, row in enumerate(values[:20]):
        if "Action Item" in row:
            header_index = i
            break

    if header_index is None:
        raise Exception("Could not detect header row")

    headers = values[header_index]
    data = values[header_index + 1:]

    # 🚨 REMOVE EMPTY FIRST COLUMN IF EXISTS
    if headers[0] == "":
        headers = headers[1:]
        data = [row[1:] for row in data]

    df = pd.DataFrame(data, columns=headers)

    # Ensure constant columns exist
    for col in CONSTANT_COLUMNS:
        if col not in df.columns:
            if col == "Snapshot Date":
                df[col] = pd.to_datetime(datetime.today().date())
            else:
                df[col] = ""

    df = df[CONSTANT_COLUMNS]

    # Parse Snapshot Date column
    if "Snapshot Date" in df.columns:
        df["Snapshot Date"] = pd.to_datetime(df["Snapshot Date"], errors="coerce", dayfirst=True)
        df["Snapshot Date"] = df["Snapshot Date"].fillna(pd.to_datetime(datetime.today().date()))

    # Clean ETA
    df["ETA / Follow-up"] = clean_eta_column(df["ETA / Follow-up"])

    # Clean Status mapping
    df["Status"] = df["Status"].replace({
        "In Progress": "🟡 In Progress",
        "At Risk": "🔴 At Risk",
        "Closed": "⚫ Closed",
        "Ongoing": "🟢 Ongoing"
    })

    return df


# ==========================================================
# SAVE SHEET
# ==========================================================

def save_master_sheet(sheet_url, df):
    gc = get_gspread_client()
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1

    df_to_save = df.copy()

    # Move Snapshot Date to first column if it exists, otherwise add it
    if "Snapshot Date" in df_to_save.columns:
        # Move to front
        cols = df_to_save.columns.tolist()
        cols.remove("Snapshot Date")
        df_to_save = df_to_save[["Snapshot Date"] + cols]
        # Update date values to today if needed
        df_to_save["Snapshot Date"] = df_to_save["Snapshot Date"].fillna(datetime.today().strftime("%d/%m/%Y"))
    else:
        # Add at front
        df_to_save.insert(0, "Snapshot Date", datetime.today().strftime("%d/%m/%Y"))
    
    # Format ETA column if it exists
    if "ETA / Follow-up" in df_to_save.columns:
        df_to_save["ETA / Follow-up"] = df_to_save["ETA / Follow-up"].apply(
            lambda x: pd.to_datetime(x).strftime("%d/%m/%Y") if pd.notnull(x) else ""
        )

    ws.clear()
    ws.update(
        [df_to_save.columns.tolist()] +
        df_to_save.fillna("").astype(str).values.tolist()
    )

# ==========================================================
# CREATE NEW GOOGLE SHEET
# ==========================================================

def create_new_sheet(df, sheet_name=None):
    """Creates a new Google Sheet with the dataframe content"""
    gc = get_gspread_client()
    
    if sheet_name is None:
        # Generate sheet name with timestamp
        from datetime import datetime
        sheet_name = f"Daily Update - {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    
    # Create new spreadsheet
    sh = gc.create(sheet_name)
    ws = sh.sheet1
    
    df_to_save = df.copy()

    # Move Snapshot Date to first column if it exists, otherwise add it
    if "Snapshot Date" in df_to_save.columns:
        cols = df_to_save.columns.tolist()
        cols.remove("Snapshot Date")
        df_to_save = df_to_save[["Snapshot Date"] + cols]
        df_to_save["Snapshot Date"] = df_to_save["Snapshot Date"].apply(
            lambda x: pd.to_datetime(x).strftime("%d/%m/%Y") if pd.notnull(x) else ""
        )
    else:
        df_to_save.insert(0, "Snapshot Date", datetime.today().strftime("%d/%m/%Y"))
    
    # Format ETA column if it exists
    if "ETA / Follow-up" in df_to_save.columns:
        df_to_save["ETA / Follow-up"] = df_to_save["ETA / Follow-up"].apply(
            lambda x: pd.to_datetime(x).strftime("%d/%m/%Y") if pd.notnull(x) else ""
        )

    # Update the new sheet with data
    ws.update(
        [df_to_save.columns.tolist()] +
        df_to_save.fillna("").astype(str).values.tolist()
    )
    
    # Share with user (optional - set to "anyone with the link" can view)
    sh.share('', perm_type='anyone', role='reader')
    
    return sh.url

# ==========================================================
# SESSION
# ==========================================================

if "master_df" not in st.session_state:
    st.session_state.master_df = None

if "sheet_url" not in st.session_state:
    st.session_state.sheet_url = None

if "auth_client" not in st.session_state:
    st.session_state.auth_client = None

if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

# ==========================================================
# CONNECT GOOGLE SHEET
# ==========================================================

st.markdown("### 🔗 Connect Google Sheet")
st.caption("Auth runtime: v2.1 (service-account first)")

# Initialize authentication state
if "auth_client" not in st.session_state:
    st.session_state.auth_client = None

if "auth_status" not in st.session_state:
    st.session_state.auth_status = False

# Show auth button if not authorized
if not st.session_state.auth_status:
    st.info("""
    **Step 1: Authorize Google Sheets access**

    In Streamlit Cloud, this uses your configured service account secrets.
    In local development, this may open Google OAuth in your browser.
    """)

    if st.button("Authorize Google Access", use_container_width=True, key="login_btn"):
        try:
            with st.spinner("Authorizing Google access..."):
                from google_auth import get_gspread_client
                st.session_state.auth_client = get_gspread_client()
                st.session_state.auth_status = True
            st.success("Access authorized successfully")
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
else:
    st.success("Google access authorized")

    st.markdown("**Step 2: Connect your Google Sheet**")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        sheet_url = st.text_input("Paste Google Sheet URL", placeholder="https://docs.google.com/spreadsheets/d/...")
    with col2:
        st.write("")
        st.write("")
        connect_btn = st.button("Connect", use_container_width=True)

    if connect_btn:
        if not sheet_url:
            st.error("Please enter a Google Sheet URL")
        else:
            try:
                with st.spinner("Connecting to Google Sheet..."):
                    st.session_state.master_df = load_master_sheet(sheet_url)
                    st.session_state.sheet_url = sheet_url
                st.success("✅ Connected successfully!")
            except Exception as e:
                error_msg = str(e)
                st.error("❌ Connection failed!")
                if "403" in error_msg or "permission" in error_msg.lower():
                    st.error("""
                    **Permission Denied!**
                    
                    Make sure:
                    1. You own this Google Sheet or have access to it
                    2. The sheet ID in the URL is correct
                    3. If using service account auth, share the sheet with that service account email
                    """)
                elif "not found" in error_msg.lower() or "404" in error_msg:
                    st.error("Sheet URL not found or is invalid. Please check the URL and try again.")
                else:
                    st.error(f"Error: {error_msg}")
    
    # Reset auth button
    if st.button("Reset Google Access", use_container_width=False):
        st.session_state.auth_client = None
        st.session_state.auth_status = False
        st.session_state.master_df = None
        st.session_state.sheet_url = None
        st.success("Google access reset successfully")
        st.rerun()

# ==========================================================
# MASTER TABLE
# ==========================================================

if st.session_state.master_df is not None:

    st.markdown("---")
    st.markdown("### 📋 Master Task Table (Editable)")

    edited_df = st.data_editor(
        st.session_state.master_df,
        num_rows="dynamic",
        width="stretch",
        key="master_table_editor",
        column_config={
            "Snapshot Date": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "ETA / Follow-up": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Status": st.column_config.SelectboxColumn(
                options=STATUS_OPTIONS
            )
        },
        hide_index=False
    )

    # Save and control buttons
    st.markdown("---")
    st.markdown("""
    **💡 New Workflow:** Load data from your Google Sheet → Edit tasks below → Click Save to create a NEW Google Sheet with your edited data.
    No permission issues, and you keep the original sheet intact!
    """)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    # Snapshot date picker
    st.markdown("**📅 Select Snapshot Date**")
    snapshot_date = st.date_input(
        "Choose date for this snapshot",
        value=datetime.today().date(),
        key="snapshot_date_picker"
    )
    
    with col1:
        if st.button("💾 Save Snapshot", use_container_width=True):

            if edited_df.empty:
                st.warning("⚠️ Nothing to save.")
            else:
                try:
                    with st.spinner("Creating new Google Sheet..."):
                        # Use selected date instead of today
                        selected_date = pd.to_datetime(snapshot_date)

                        # Inject snapshot date
                        edited_df["Snapshot Date"] = selected_date

                        # Update session state
                        st.session_state.master_df = edited_df

                        # Create NEW Google Sheet instead of updating
                        new_sheet_url = create_new_sheet(
                            edited_df, 
                            f"Daily Update - {selected_date.strftime('%d-%m-%Y')}"
                        )

                    st.success(f"✅ New sheet created for {selected_date.strftime('%d/%m/%Y')}")
                    st.markdown(f"**📊 New Sheet URL:** [Open Sheet]({new_sheet_url})")
                    
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ Failed to create sheet: {error_msg}")
                    if "quota" in error_msg.lower():
                        st.warning("You've reached your Google Drive quota. Please delete some files and try again.")
                    else:
                        st.info("Make sure you have Google authentication set up correctly.")

    st.session_state.master_df = edited_df

# ==========================================================
# TIMELINE VIEW
# ==========================================================

if st.session_state.master_df is not None:

    df = st.session_state.master_df.copy()

    st.markdown("---")
    st.header("🗓️ Intelligent Timeline View")

    if df.empty:
        st.info("No data available.")
    else:

        df = df.sort_values(by="Snapshot Date")

        # ============================================
        # FILTERS SECTION
        # ============================================
        st.markdown("### 🔍 Filter Tasks")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        # Status Filter
        with filter_col1:
            selected_statuses = st.multiselect(
                "📊 Filter by Status",
                options=STATUS_OPTIONS,
                default=STATUS_OPTIONS,
                key="status_filter"
            )
        
        # Owner/Person Filter
        with filter_col2:
            # Extract individual names from combined owner fields
            all_individual_owners = set()
            for owner in df["Owner"].unique():
                if owner and str(owner).strip():
                    # Split by "/" to get individual names
                    names = str(owner).split("/")
                    for name in names:
                        cleaned_name = name.strip()
                        if cleaned_name:
                            all_individual_owners.add(cleaned_name)
            
            all_individual_owners = sorted(list(all_individual_owners))
            
            selected_owners = st.multiselect(
                "👤 Filter by Owner",
                options=all_individual_owners,
                default=all_individual_owners,
                key="owner_filter"
            )
        
        # Date Filter
        with filter_col3:
            # Get min/max ETA dates for the filter range
            eta_dates = pd.to_datetime(df["ETA / Follow-up"], errors='coerce')
            min_eta = eta_dates.min().date()
            max_eta = eta_dates.max().date()
            
            date_range = st.date_input(
                "📅 Filter by ETA Date",
                value=(min_eta, max_eta),
                min_value=min_eta,
                max_value=max_eta,
                key="date_filter"
            )

        # Apply filters
        # Status filter - exact match
        status_mask = df["Status"].isin(selected_statuses)
        
        # Owner filter - substring/partial match (so "Balan" matches "Balan / Praveen")
        if selected_owners:
            owner_mask = df["Owner"].apply(
                lambda x: any(owner in str(x) for owner in selected_owners)
            )
        else:
            owner_mask = pd.Series([True] * len(df))
        
        # Date filter - by ETA / Follow-up dates
        try:
            if isinstance(date_range, (tuple, list)):
                start_date = date_range[0]
                end_date = date_range[1]
            else:
                start_date = end_date = date_range
            
            # Convert ETA / Follow-up to dates for comparison
            df_eta_dates = pd.to_datetime(df["ETA / Follow-up"], errors='coerce').dt.date
            
            # Compare using boolean mask
            date_mask = (df_eta_dates >= start_date) & (df_eta_dates <= end_date)
        except Exception as e:
            st.error(f"Date filter error: {str(e)}")
            date_mask = pd.Series([True] * len(df))
        
        filtered_df = df[status_mask & owner_mask & date_mask]

        st.markdown("")  # Spacing

        # Show filter results
        result_count = len(filtered_df)
        if result_count == 0:
            st.warning("🔍 No tasks match your filters. Try adjusting your selection.")
        else:
            st.success(f"✅ Showing {result_count} task(s) matching your filters")

        if len(filtered_df) > 0:
            # Prepare data for display with styling
            display_df = filtered_df.copy()
            display_df["Snapshot Date"] = display_df["Snapshot Date"].dt.strftime("%d/%m/%Y")
            display_df["ETA / Follow-up"] = display_df["ETA / Follow-up"].dt.strftime("%d/%m/%Y")
            
            # Reorder columns for better visibility
            columns_order = [
                "Snapshot Date",
                "Status",
                "Category",
                "Action Item",
                "Owner",
                "Client / Partner",
                "ETA / Follow-up",
                "Notes / Completion Callout"
            ]
            
            display_df = display_df[[col for col in columns_order if col in display_df.columns]]
            
            # Rename for better display
            display_df.columns = [
                "Date",
                "Status",
                "Category",
                "Task",
                "Owner",
                "Client",
                "ETA",
                "Notes"
            ]
            
            # Add styling with custom HTML table for compact display
            st.markdown("""
            <style>
                .status-section {
                    margin-bottom: 24px;
                }
                
                .status-header {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    padding: 16px;
                    background: linear-gradient(135deg, rgba(199, 210, 254, 0.3) 0%, rgba(221, 214, 254, 0.3) 100%);
                    border-left: 4px solid #A78BFA;
                    border-radius: 8px;
                    margin-bottom: 16px;
                    border: 1px solid rgba(199, 210, 254, 0.5);
                    font-weight: 600;
                    color: #5F5952;
                }
                
                .task-table {
                    width: 100%;
                    border-collapse: collapse;
                    background: var(--color-white);
                    border: 1px solid #F3E8FF;
                    border-radius: 8px;
                    overflow: hidden;
                    margin-bottom: 20px;
                    box-shadow: 0 1px 3px 0 rgba(167, 139, 250, 0.1);
                }
                
                .task-table th {
                    background: #F3E8FF;
                    color: #5F5952;
                    padding: 12px 16px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 13px;
                    border-bottom: 2px solid #C7D2FE;
                    letter-spacing: 0.5px;
                }
                
                .task-table td {
                    padding: 12px 16px;
                    border-bottom: 1px solid #F3E8FF;
                    color: #5F5952;
                    font-size: 13px;
                }
                
                .task-table tbody tr:hover {
                    background: #FFFBF0;
                    transition: background-color 150ms cubic-bezier(0.4, 0, 0.2, 1);
                }
                
                .task-table tbody tr:last-child td {
                    border-bottom: none;
                }
                
                .task-name {
                    font-weight: 500;
                    color: #A78BFA;
                }
                
                .owner-cell {
                    font-size: 12px;
                    color: #8B8680;
                }
                
                .notes-cell {
                    font-size: 12px;
                    color: #A8A0A0;
                    font-style: italic;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Summary stats row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                in_progress = len(filtered_df[filtered_df["Status"].str.contains("In Progress|in progress", na=False)])
                st.metric("🟡 In Progress", in_progress)
            with col2:
                at_risk = len(filtered_df[filtered_df["Status"].str.contains("At Risk|at risk", na=False)])
                st.metric("🔴 At Risk", at_risk)
            with col3:
                closed = len(filtered_df[filtered_df["Status"].str.contains("Closed|closed", na=False)])
                st.metric("⚫ Closed", closed)
            with col4:
                ongoing = len(filtered_df[filtered_df["Status"].str.contains("Ongoing|ongoing", na=False)])
                st.metric("🟢 Ongoing", ongoing)
            
            st.markdown("---")
            
            # Group by status and display as individual tables
            status_order = ["🟡 In Progress", "🔴 At Risk", "⚫ Closed", "🟢 Ongoing"]
            status_colors = {
                "🟡 In Progress": "#FFA500",
                "🔴 At Risk": "#FF6B6B",
                "⚫ Closed": "#4A5568",
                "🟢 Ongoing": "#51CF66"
            }
            
            for status in status_order:
                status_df = filtered_df[filtered_df["Status"] == status]
                
                if len(status_df) > 0:
                    # Status header
                    status_color = status_colors.get(status, "#667eea")
                    st.markdown(f"""
                    <div class="status-section">
                        <div class="status-header" style="border-left-color: {status_color};">
                            <div style="font-size: 18px;">{status}</div>
                            <div style="font-weight: 600; color: #fff; margin-left: auto;">{len(status_df)} tasks</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Prepare data for this status
                    display_status_df = status_df.copy()
                    display_status_df["Snapshot Date"] = display_status_df["Snapshot Date"].dt.strftime("%d/%m/%Y")
                    display_status_df["ETA / Follow-up"] = display_status_df["ETA / Follow-up"].dt.strftime("%d/%m/%Y")
                    
                    # Create table for this status
                    html_table = '<table class="task-table"><thead><tr>'
                    html_table += '<th>Date</th><th>Category</th><th>Task</th><th>Owner</th><th>Client</th><th>ETA</th><th>Notes</th>'
                    html_table += '</tr></thead><tbody>'
                    
                    for _, row in display_status_df.iterrows():
                        html_table += '<tr>'
                        html_table += f'<td>{row["Snapshot Date"]}</td>'
                        html_table += f'<td>{row["Category"]}</td>'
                        html_table += f'<td class="task-name">{row["Action Item"]}</td>'
                        html_table += f'<td class="owner-cell">{row["Owner"]}</td>'
                        html_table += f'<td style="font-size: 10px;">{row["Client / Partner"]}</td>'
                        html_table += f'<td style="font-weight: 500; color: #b8d4ff; font-size: 11px;">{row["ETA / Follow-up"]}</td>'
                        
                        notes = str(row["Notes / Completion Callout"])[:60] + "..." if len(str(row["Notes / Completion Callout"])) > 60 else row["Notes / Completion Callout"]
                        html_table += f'<td class="notes-cell">{notes}</td>'
                        html_table += '</tr>'
                    
                    html_table += '</tbody></table>'
                    st.markdown(html_table, unsafe_allow_html=True)

# ==========================================================
# EXPORT
# ==========================================================

if st.session_state.master_df is not None:

    st.markdown("---")
    st.markdown("### ⬇️ Export & Download")

    col1, col2 = st.columns([0.5, 1], gap="medium")
    
    csv = st.session_state.master_df.to_csv(index=False)

    with col1:
        st.download_button(
            "📥 Download CSV",
            csv,
            "timeline_export.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        st.info("💾 Export your tasks for backup or sharing", icon="📋")

