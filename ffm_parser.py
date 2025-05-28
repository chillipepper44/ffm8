def parse_manifest_to_ffm8(pdf_path):
    import fitz  # PyMuPDF

    doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])

    lines = text.splitlines()
    ffm_lines = ["FFM/8"]
    current_uld = ""
    buffer = []
    cargos = []
    
    def flush_buffer():
        nonlocal buffer, current_uld
        if len(buffer) < 6:
            buffer.clear()
            return

        try:
            awb_line = buffer[0]
            pieces_line = buffer[1]
            weight_line = buffer[2]
            desc_line = buffer[3]
            shc_line = buffer[4]
            route_line = buffer[5]

            awb = awb_line.replace(" ", "")
            pcs_raw = pieces_line.strip()
            pcs_val = pcs_raw.split("/")[0]
            pcs_type = "S" if "/" in pcs_raw else "T"

            weight = weight_line.split("/")[0].strip()
            weight_f = float(weight)
            mc = round(weight_f * 0.006, 2)

            desc = f"{desc_line.strip()} {shc_line.strip()}".strip().replace("  ", " ")
            route = route_line.replace(" ", "").replace("-", "")
            if len(route) >= 6:
                origin, dest = route[:3], route[-3:]
            else:
                origin, dest = "XXX", "XXX"

            extra = f"T{pcs_raw.split('/')[1]}" if "/" in pcs_raw else ""
            formatted = f"{awb}{origin}{dest}/{pcs_type}{pcs_val}K{weight_f:.2f}MC{mc}{extra}"
            if desc:
                formatted += f"/{desc.replace(' ', ' ', 1)}"
            if current_uld:
                cargos.append(f"ULD/{current_uld}")
                current_uld = ""
            cargos.append(formatted)
        except Exception:
            pass
        buffer.clear()

    for line in lines:
        line = line.strip()
        if not line or any(skip in line for skip in ["Cargo Manifest", "Owner", "SECURITY PASSED", "Total:", "Page", "kg", "Date/STD", "Point of Loading"]):
            continue
        if line.upper().startswith(("ULD", "PMC", "FLA", "PKC")):
            flush_buffer()
            current_uld = line.strip()
        elif line.replace(" ", "").startswith(("555", "800")):
            flush_buffer()
            buffer = [line]
        elif buffer:
            buffer.append(line)
    flush_buffer()

    # Combine with ULD appearing only once
    seen_uld = set()
    for line in cargos:
        if line.startswith("ULD/"):
            if line not in seen_uld:
                ffm_lines.append(line)
                seen_uld.add(line)
        else:
            ffm_lines.append(line)

    return "\n".join(ffm_lines)
