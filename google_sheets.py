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


# =====================================================
# FORMAT ETA COLUMN WITH DARKER COLOR
# =====================================================

def format_eta_column(sheet_url: str):
    """
    Apply darker background color to ETA/Follow-up column in Google Sheet
    """
    gc = get_gspread_client()
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1

    # Get header row to find ETA column
    headers = ws.row_values(1)
    
    eta_col_index = None
    for idx, header in enumerate(headers):
        if "ETA" in header or "Follow-up" in header:
            eta_col_index = idx + 1  # gspread uses 1-indexed columns
            break
    
    if eta_col_index is None:
        raise Exception("Could not find ETA column")
    
    # Get the number of rows with data
    all_values = ws.get_all_values()
    num_rows = len(all_values)
    
    # Build the range for the entire ETA column (excluding header)
    col_letter = chr(64 + eta_col_index)  # Convert 1-indexed column to letter
    range_to_format = f"{col_letter}2:{col_letter}{num_rows}"
    
    # Format the entire ETA column with darker blue background
    requests = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": ws.id,
                    "startRowIndex": 1,  # Start from row 2 (skip header)
                    "startColumnIndex": eta_col_index - 1,
                    "endColumnIndex": eta_col_index
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.25,
                            "green": 0.45,
                            "blue": 0.85
                        },
                        "textFormat": {
                            "bold": True,
                            "foregroundColor": {
                                "red": 1.0,
                                "green": 1.0,
                                "blue": 1.0
                            }
                        }
                    }
                },
                "fields": "userEnteredFormat"
            }
        }
    ]
    
    sh.batch_update({"requests": requests})
