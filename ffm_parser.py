import fitz  # PyMuPDF

def parse_manifest_to_ffm8(pdf_file):
    ffm_lines = ["FFM/8"]
    uld_lines = []
    cargo_lines = []

    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    lines = text.splitlines()
    current_uld = ""
    buffer = []

    def flush_buffer():
        nonlocal buffer, current_uld
        if len(buffer) >= 6:
            try:
                awb = buffer[0].replace(" ", "").strip()
                pieces = buffer[1].strip()
                piece_type = "P" if "/" in pieces else "T"
                pieces_val = pieces.split("/")[0]

                weight_raw = buffer[2].strip()
                weight = weight_raw.split("/")[0]
                mc = round(float(weight) * 0.006, 2)

                desc = buffer[3].strip()
                shc = buffer[4].strip()
                description = f"{desc} {shc}".strip()

                route = buffer[5].replace(" ", "").replace("-", "").strip()
                if len(route) >= 6:
                    origin = route[:3]
                    dest = route[-3:]
                else:
                    origin = "XXX"
                    dest = "XXX"

                line = f"{awb}{origin}-{dest}/{piece_type}{pieces_val}K{weight}MC{mc}"
                if "/" in pieces:
                    part = pieces.split("/")[-1]
                    line += f"T{part}"
                if description:
                    line += f"/{description}"
                if current_uld:
                    cargo_lines.append(f"ULD/{current_uld}")
                    current_uld = ""
                cargo_lines.append(line)
            except Exception:
                pass
        buffer = []

    for raw in lines:
        line = raw.strip()
        if not line or any(keyword in line for keyword in [
            "Cargo Manifest", "Owner", "SECURITY PASSED", "Page", "Total:", "kg", "Registration"
        ]):
            continue
        if line.upper().startswith(("ULD", "PMC", "FLA", "PKC")):
            flush_buffer()
            current_uld = line
        elif line.replace(" ", "").startswith(("555", "800")):
            flush_buffer()
            buffer = [line]
        elif buffer:
            buffer.append(line)
    flush_buffer()

    # รวม ULD ให้แสดงก่อนแค่ครั้งเดียว
    output = []
    shown_uld = set()
    for line in cargo_lines:
        if line.startswith("ULD/"):
            if line not in shown_uld:
                output.append(line)
                shown_uld.add(line)
        else:
            output.append(line)
    return "\n".join(output)
