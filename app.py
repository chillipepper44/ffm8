from flask import Flask, request, render_template
import pdfplumber
from collections import defaultdict
import re
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)

def parse_pdf_to_ffm8(pdf_file):
    ffm_lines = ["FFM/8"]
    seen_awbs = defaultdict(int)
    current_uld = None

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})
            if not table or len(table[0]) < 12:
                continue

            for row in table:
                try:
                    col0 = row[0]
                    if col0:
                        upper_col0 = col0.strip().upper()
                        if re.match(r"^[A-Z]{3}\d{5}[A-Z]{2}$", upper_col0):
                            current_uld = f"ULD/{upper_col0}"
                            ffm_lines.append(current_uld)
                            continue
                        elif upper_col0 == "BULK":
                            current_uld = "BULK"
                            ffm_lines.append(current_uld)
                            continue

                    if not current_uld:
                        continue

                    if not isinstance(col0, str) or not re.match(r"^\d{3}\s*-\s*\d{8}$", col0.strip()):
                        continue

                    awb = re.sub(r"\s*-\s*", "-", col0.strip())
                    prefix, awb_number = awb.split("-")
                    awb_id = f"{prefix}-{awb_number}"

                    pcs_raw = row[1] or ""
                    weight_raw = row[4] or ""
                    desc_raw = row[8] or ""
                    shc_raw = row[10] or "GEN"
                    route_raw = row[11] or ""

                    pcs_left, pcs_right = pcs_raw.split("/") if "/" in pcs_raw else (pcs_raw, "")
                    weight_val = float(weight_raw.split("/")[0])
                    mc_val = Decimal(weight_val * 0.006).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    desc = desc_raw.strip()
                    shc = shc_raw.strip()
                    route = route_raw.replace(" ", "").strip()

                    if not desc or desc.upper() == shc.upper():
                        desc = shc

                    if "-" in route:
                        org, dest = route.split("-")
                    else:
                        org, dest = "XXX", "XXX"  # fallback if parsing fails

                    seen_awbs[awb_id] += 1
                    if seen_awbs[awb_id] == 1:
                        line = f"{awb_id}{org}{dest}/T{pcs_left}K{weight_val:.2f}MC{mc_val:.2f}"
                    else:
                        line = f"{awb_id}{org}{dest}/S{pcs_left}K{weight_val:.2f}MC{mc_val:.2f}"
                        if pcs_right:
                            line += f"T{pcs_right}"

                    line += f"/{desc}/{shc}"
                    ffm_lines.append(line)

                except Exception as e:
                    continue

    return "\n".join(ffm_lines)

@app.route("/", methods=["GET", "POST"])
def index():
    result_text = ""
    if request.method == "POST":
        file = request.files.get("manifest")
        if file and file.filename.lower().endswith(".pdf"):
            result_text = parse_pdf_to_ffm8(file)
    return render_template("index.html", output=result_text)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
