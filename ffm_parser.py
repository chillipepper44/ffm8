import fitz  # PyMuPDF

def parse_manifest_to_ffm8(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    ffm_lines = ["FFM/8"]

    current_uld = "XXXXXXXXXXXX"
    temp_entry = []
    results = []

    def flush_entry():
        if len(temp_entry) >= 6:
            try:
                awb_line = temp_entry[0]
                piece_line = temp_entry[1]
                weight_line = temp_entry[2]
                desc_line = temp_entry[3]
                shc_line = temp_entry[4]
                route_line = temp_entry[5]

                awb = awb_line.replace(" ", "").strip()
                pieces = piece_line.split("/")[0].strip()
                piece_type = "P" if "/" in piece_line else "T"

                weight = weight_line.split("/")[0].strip()
                mc = round(float(weight) * 0.006, 2)

                description = f"{desc_line.strip()} {shc_line.strip()}".strip().replace("  ", " ")
                route = route_line.replace(" ", "").replace("-", "").strip()
                dest = route[-3:] if len(route) >= 6 else "XXX"

                # Add T[number] if found in piece_line
                tnum = ""
                if "/" in piece_line:
                    parts = piece_line.split("/")
                    if len(parts) == 2:
                        tnum = f"T{parts[1].strip()}"

                formatted = f"{awb}{route}/{piece_type}{pieces}K{weight}MC{mc}{tnum}/{description}"
                results.append((current_uld, formatted))
            except Exception as e:
                print(f"Skip row due to error: {e} => {temp_entry}")
        temp_entry.clear()

    for page in doc:
        text = page.get_text("text")
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.upper().startswith("ULD/") or line.upper().startswith("PMC") or line.upper().startswith("FLA") or line.upper().startswith("PKC"):
                flush_entry()
                current_uld = line.strip().replace("ULD/", "").upper()
                ffm_lines.append(f"ULD/{current_uld}")
            elif line.startswith("555") or line.startswith("800") or line.startswith("331"):
                flush_entry()
                temp_entry.append(line)
            else:
                temp_entry.append(line)

    flush_entry()

    for uld, line in results:
        ffm_lines.append(line)

    return "\n".join(ffm_lines)
