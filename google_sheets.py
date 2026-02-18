import gspread
import pandas as pd
from google_auth import get_gspread_client


# =====================================================
# SMART GOOGLE SHEET LOADER (AUTO HEADER DETECTION)
# =====================================================

def load_sheet(sheet_url: str) -> pd.DataFrame:
    gc = get_gspread_client()
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1

    values = ws.get_all_values()

    if not values:
        return pd.DataFrame()

    # -------------------------------------------------
    # FIND HEADER ROW (row containing "Action Item")
    # -------------------------------------------------
    header_row_index = None

    for i, row in enumerate(values[:20]):  # scan first 20 rows
        if any("Action Item" in str(cell) for cell in row):
            header_row_index = i
            break

    if header_row_index is None:
        raise Exception("Could not detect header row. Make sure 'Action Item' column exists.")

    headers = values[header_row_index]
    data = values[header_row_index + 1 :]

    # -------------------------------------------------
    # CLEAN HEADERS
    # -------------------------------------------------
    seen = {}
    clean_headers = []

    for idx, h in enumerate(headers):
        h = h.strip() if h else ""

        # Replace empty header names
        if h == "":
            h = f"Column_{idx}"

        # Make duplicates unique
        if h in seen:
            seen[h] += 1
            h = f"{h}_{seen[h]}"
        else:
            seen[h] = 0

        clean_headers.append(h)

    df = pd.DataFrame(data, columns=clean_headers)

    # -------------------------------------------------
    # REMOVE FULLY EMPTY COLUMNS
    # -------------------------------------------------
    df = df.loc[:, ~(df == "").all()]

    # -------------------------------------------------
    # REMOVE FULLY EMPTY ROWS
    # -------------------------------------------------
    df = df.replace("", pd.NA)
    df = df.dropna(how="all")
    df = df.fillna("")

    return df


# =====================================================
# SAVE BACK TO GOOGLE SHEET
# =====================================================

def save_sheet(sheet_url: str, df: pd.DataFrame):
    gc = get_gspread_client()
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1

    ws.clear()

    ws.update(
        [df.columns.tolist()] + df.astype(str).values.tolist()
    )
