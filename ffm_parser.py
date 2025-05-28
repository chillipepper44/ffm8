import pdfplumber
from collections import defaultdict
import re

def parse_manifest_to_ffm8(pdf_path):
    current_section = None  # Either ULD/XXX or "Bulk"
    results = ["FFM/8"]
    awb_counter = defaultdict(int)

    def format_awb_line(awb, pcs, weight, desc, shc, route):
        awb_counter[awb] += 1
        piece_type = "T" if awb_counter[awb] == 1 else "S"
        mc = round(float(weight) * 0.006, 2)
        pcs_left, pcs_right = (pcs.split("/") if "/" in pcs else (pcs, ""))

        line = f"{awb}{route}/{piece_type}{pcs_left}K{weight}MC{mc:.2f}"
        if pcs_right:
            line += f"T{pcs_right}"
        line += f"/{desc}/{shc}"
        return line

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            for row in table:
                if not row or all(cell is None or cell.strip() == "" for cell in row):
                    continue

                col0 = (row[0] or "").strip()
                if not col0:
                    continue

                # ตรวจจับว่าเป็น ULD หรือ Bulk
                if re.match(r"^[A-Z]{3}\d{5}[A-Z]{2}$", col0):
                    current_section = f"ULD/{col0}"
                    results.append(current_section)
                    continue
                elif col0.upper() == "BULK":
                    current_section = "Bulk"
                    results.append(current_section)
                    continue

                # ตรวจจับว่าเป็น AWB
                awb_match = re.match(r"(\d{3})\s*-\s*(\d{8})", col0)
                if awb_match and current_section:
                    prefix, number = awb_match.groups()
                    awb = f"{prefix}-{number}"

                    pcs = (row[1] or "").strip()
                    weight = (row[4] or "").strip()
                    desc = (row[8] or "").strip()
                    shc = (row[10] or "").strip()
                    route = (row[11] or "").strip().replace(" ", "").replace("-", "")

                    if not all([pcs, weight, desc, shc, route]):
                        continue  # ข้ามถ้าข้อมูลไม่ครบ

                    if desc.upper() == shc.upper():
                        desc = shc  # ลบข้อมูลซ้ำ

                    formatted_line = format_awb_line(awb.replace("-", ""), pcs, weight, desc, shc, route)
                    results.append(formatted_line)

    return "\n".join(results)
