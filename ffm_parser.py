# ffm_parser.py

import fitz  # PyMuPDF
import re
import csv

def is_valid_awb(text):
    return bool(re.match(r"^\d{3} ?- ?\d{8}$", text.strip()))

def extract_float(s):
    try:
        return float(s.strip())
    except:
        return None

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def parse_manifest_to_ffm8(file):
    file.stream.seek(0)  # Ensure reading from start
    doc = fitz.open(stream=file.stream.read(), filetype="pdf")
    lines = []
    for page in doc:
        text = page.get_text().split("\n")
        lines.extend(text)

    ffm_lines = ["FFM/8"]
    current_uld = None
    buffer = []

    for i, line in enumerate(lines):
        line = line.strip()
        if (
            not line
            or line.lower().startswith("prepared by")
            or "security passed" in line.lower()
            or line.lower() in ["owner", "weight", "pieces", "destination"]  # Add more as needed
        ):
            continue

        if re.match(r"^[A-Z]{3}\d{5,}", line):
            current_uld = line.strip().upper()
            ffm_lines.append(f"ULD/{current_uld}")
            continue

        if is_valid_awb(line):
            if buffer:
                ffm_lines.append(format_entry(buffer))
                buffer = []
            buffer = [line]
        else:
            if buffer:
                buffer.append(line)

    if buffer:
        ffm_lines.append(format_entry(buffer))

    return "\n".join(ffm_lines)


def format_entry(lines):
    awb_line = lines[0]
    parts = awb_line.replace(" ", "").split("-")
    awb = f"{parts[0]}-{parts[1]}" if len(parts) == 2 else awb_line.strip()

    pieces = ""
    weight = ""
    dest = ""
    shc = ""
    desc = []

    for line in lines[1:]:
        line = line.strip()
        # Look for PIECES and WEIGHT
        if re.match(r"^\d+(\/\d+)?$", line):
            pieces = line
        elif re.match(r"^\d+(\.\d+)?(\/\d+(\.\d+)?)?$", line):
            weight = line.split("/")[0]
        elif re.match(r"^[A-Z]{3} ?- ?[A-Z]{3}$", line):
            dest = line.replace(" ", "")
        elif line in ["GEN", "ELM", "ELI"]:
            shc = line
        else:
            desc.append(line)

    # Extra check: weight must be a valid float
    def is_float(val):
        try:
            float(val)
            return True
        except Exception:
            return False

    if not awb or not pieces or not weight or not dest or not is_float(weight):
        return f"{awb}XXXXXXXXXXXX/P{pieces}K{weight}/{' '.join(desc)}"

    # Determine if P or T
    ptype = "P" if "/" in pieces else "T"
    pcs = pieces.split("/")[0] if "/" in pieces else pieces
    weight_val = float(weight)
    mc = round(weight_val * 0.006, 2)
    mc = f"{mc:.2f}"

    weight_str = f"{int(weight_val)}" if weight_val.is_integer() else f"{weight_val:.3f}"

    detail = f"{awb}{dest}/" \
             f"{ptype}{pcs}K{weight_str}MC{mc}"

    if "/" in pieces:
        detail += f"T{pieces.split('/')[1]}"

    if desc:
        detail += f"/{' '.join(desc)}"
    if shc:
        detail += f"/{shc}"

    return detail
