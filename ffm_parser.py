
import fitz
from collections import defaultdict
import re

def parse_manifest_to_ffm8(pdf_path):
    doc = fitz.open(pdf_path)
    lines_with_y = defaultdict(list)

    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    y0 = round(line["bbox"][1], 1)
                    for span in line["spans"]:
                        x0 = span["bbox"][0]
                        text = span["text"].strip()
                        if text:
                            lines_with_y[y0].append((x0, text))

    structured_lines = []
    for y in sorted(lines_with_y.keys()):
        spans = sorted(lines_with_y[y], key=lambda x: x[0])
        structured_lines.append(" ".join([text for _, text in spans]))

    results = ["FFM/8"]
    awb_counter = defaultdict(int)
    current_uld = None
    uld_inserted = set()
    cargo_lines = []
    bulk_lines = []
    in_bulk = False

    awb_regex = re.compile(
        r"^(555|800)\s*-\s*(\d+)\s+(\d+(?:/\d+)?)\s+([\d.]+)(?:/[\d.]+)?\s+(.*?)\s+([A-Z]{3})\s*-\s*([A-Z]{3})$"
    )

    for line in structured_lines:
        line = line.strip()
        if not line:
            continue

        if line.upper() == "BULK":
            in_bulk = True
            continue

        if re.match(r"^[A-Z]{3}\d{5}[A-Z]{2}$", line):
            current_uld = f"ULD/{line}"
            in_bulk = False
            continue

        match = awb_regex.match(line)
        if match:
            prefix, awb_number, pcs_raw, weight_raw, desc, org, dest = match.groups()
            awb = f"{prefix}{awb_number}"
            awb_counter[awb] += 1

            pcs_left, pcs_right = pcs_raw.split("/") if "/" in pcs_raw else (pcs_raw, "")
            weight_val = float(weight_raw)
            mc = round(weight_val * 0.006, 2)
            piece_type = "S" if awb_counter[awb] > 1 else "T"

            formatted = f"{prefix}-{awb_number}{org}{dest}/{piece_type}{pcs_left}K{weight_val}MC{mc}"
            if pcs_right:
                formatted += f"T{pcs_right}"
            formatted += f"/{desc}/{dest}"

            if in_bulk:
                bulk_lines.append(formatted)
            else:
                if current_uld and current_uld not in uld_inserted:
                    cargo_lines.append(current_uld)
                    uld_inserted.add(current_uld)
                cargo_lines.append(formatted)

    doc.close()
    return "\n".join(results + bulk_lines + cargo_lines)
