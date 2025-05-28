import pdfplumber
import pandas as pd
import re
from collections import defaultdict

def parse_manifest_to_ffm8(pdf_path):
    # ดึงคำจากทุกหน้า
    all_words = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(x_tolerance=1, y_tolerance=2, keep_blank_chars=True)
            for word in words:
                all_words.append({
                    "page": page_num + 1,
                    "x": float(word["x0"]),
                    "y": round(float(word["top"]), 1),
                    "text": word["text"].strip()
                })

    df_words = pd.DataFrame(all_words)

    # กำหนดช่วงของ x สำหรับแต่ละคอลัมน์
    column_ranges = {
        "col0": (0, 100),
        "col1": (100, 150),
        "col4": (250, 320),
        "col8": (500, 600),
        "col10": (650, 700),
        "col11": (700, 800),
    }

    # แยกข้อความเข้าแถวตาม y
    rows_by_y = {}
    for _, row in df_words.iterrows():
        x, y, text = row["x"], row["y"], row["text"]
        col_name = None
        for col, (x_min, x_max) in column_ranges.items():
            if x_min <= x < x_max:
                col_name = col
                break
        if col_name:
            if y not in rows_by_y:
                rows_by_y[y] = {col: "" for col in column_ranges}
            rows_by_y[y][col_name] += " " + text

    # แปลงเป็น DataFrame
    structured_rows = []
    for y, cols in rows_by_y.items():
        row_data = {"y": y}
        row_data.update({col: val.strip() for col, val in cols.items()})
        structured_rows.append(row_data)
    df_structured = pd.DataFrame(structured_rows).sort_values(by="y").reset_index(drop=True)

    # สร้าง FFM/8 Output
    results = ["FFM/8"]
    current_uld = None
    seen_aman = defaultdict(int)
    uld_blocks = defaultdict(list)

    for _, row in df_structured.iterrows():
        raw = row.get("col0", "").strip()

        if raw.upper().startswith("ULD") or re.match(r"^[A-Z]{3}\d{5}[A-Z]{2}$", raw):
            current_uld = f"ULD/{raw}" if not raw.startswith("ULD/") else raw
            continue

        if raw.upper() == "BULK":
            current_uld = "Bulk"
            continue

        if re.match(r"^\d{3}\s*-\s*\d{8}$", raw) or re.match(r"^\d{11}$", raw.replace(" ", "")):
            aman = raw.replace(" ", "").replace("-", "")
            pcs = row.get("col1", "").strip()
            weight = row.get("col4", "").strip()
            desc = row.get("col8", "").strip()
            shc = row.get("col10", "").strip()
            route = row.get("col11", "").replace(" ", "").replace("-", "")

            if not pcs or not weight or not route:
                continue

            pcs_left, pcs_right = pcs.split("/") if "/" in pcs else (pcs, "")
            try:
                weight_val = float(weight.split("/")[0]) if "/" in weight else float(weight)
            except ValueError:
                continue
            mc = round(weight_val * 0.006, 2)

            if desc.upper() == shc.upper():
                desc = shc

            piece_type = "S" if seen_aman[aman] else "T"
            seen_aman[aman] += 1

            formatted = f"{aman}{route}/"
            if piece_type == "S":
                formatted += f"S{pcs_left}K{weight_val:.2f}MC{mc:.2f}"
                if pcs_right:
                    formatted += f"T{pcs_right}"
            else:
                formatted += f"T{pcs_left}K{weight_val:.2f}MC{mc:.2f}"

            formatted += f"/{desc}/{shc}"

            uld_blocks[current_uld].append(formatted)

    for uld, lines in uld_blocks.items():
        results.append(uld)
        results.extend(lines)

    return "\n".join(results)
