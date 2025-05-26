# ffm_parser.py

import fitz  # PyMuPDF

def parse_manifest_to_ffm8(file):
    ffm_lines = []
    uld_section = None
    buffer = []

    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for ULD line
        if line.upper().startswith("PMC") or line.upper().startswith("PKC") or line.upper().startswith("FLA"):
            if buffer:
                ffm_lines.extend(process_buffer(buffer, uld_section))
                buffer = []
            uld_section = line.strip()
        else:
            buffer.append(line)
        i += 1

    # Process any remaining buffer
    if buffer:
        ffm_lines.extend(process_buffer(buffer, uld_section))

    return "FFM/8\n" + "\n".join(ffm_lines)


def process_buffer(lines, uld):
    entries = []
    i = 0
    while i < len(lines) - 5:
        awb_line = lines[i]
        piece_line = lines[i + 1]
        weight_line = lines[i + 2]
        desc_line = lines[i + 3]
        shc_line = lines[i + 4]
        route_line = lines[i + 5]

        try:
            if not awb_line or not piece_line or not weight_line or not route_line:
                i += 1
                continue

            awb = awb_line.replace(" ", "").strip()
            pieces = piece_line.strip().split("/")[0]
            piece_type = "P" if "/" in piece_line else "T"

            weight = weight_line.split("/")[0].strip()
            try:
                weight_val = float(weight)
            except ValueError:
                i += 1
                continue
            mc = round(weight_val * 0.006, 2)

            route = route_line.replace(" ", "").replace("-", "").strip()
            dest = route[-3:] if len(route) >= 6 else "XXX"

            description = f"{desc_line.strip()} {shc_line.strip()}".strip()

            line = f"{awb}{route}/" \
                   f"{piece_type}{pieces}K{weight}" \
                   f"MC{mc}"

            if "/" in piece_line:
                part_total = piece_line.split("/")[1]
                line += f"T{part_total}"

            if description:
                line += f"/{description}"

            if uld:
                entries.append(f"ULD/{uld.upper()}")
            entries.append(line)
        except Exception:
            pass
        i += 6

    return entries
