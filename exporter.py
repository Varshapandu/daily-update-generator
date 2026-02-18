# import pandas as pd
# import io

# def export_to_excel(df: pd.DataFrame) -> bytes:
#     """
#     Export DataFrame to Excel format
#     Returns bytes for download
#     """
#     buffer = io.BytesIO()
#     with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="Daily Update")
#     buffer.seek(0)
#     return buffer.getvalue()


# def export_to_csv(df: pd.DataFrame) -> bytes:
#     """
#     Export DataFrame to CSV format
#     Returns bytes for download
#     """
#     return df.to_csv(index=False).encode("utf-8")

import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch


# --------------------------------------------------
# EXPORT TO EXCEL
# --------------------------------------------------
def export_to_excel(df: pd.DataFrame):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


# --------------------------------------------------
# EXPORT TO CSV
# --------------------------------------------------
def export_to_csv(df: pd.DataFrame):
    return df.to_csv(index=False).encode("utf-8")


# --------------------------------------------------
# EXPORT TO PDF
# --------------------------------------------------
def export_to_pdf(df: pd.DataFrame):

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4
    )

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Daily Update Timeline", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Convert DataFrame to list
    data = [df.columns.tolist()] + df.astype(str).values.tolist()

    table = Table(data)

    table.setStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ])

    elements.append(table)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
