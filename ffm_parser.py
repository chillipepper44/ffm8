import fitz  # PyMuPDF

def parse_manifest_to_ffm8(pdf_file):
    ffm_lines = ["FFM/8"]
    current_uld = None
    lines = []

    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text = page.get_text()
            blocks = text.split("\n")

            buffer = []
            for line in blocks:
                if line.strip() == "":
                    continue
                buffer.append(line.strip())

                # เมื่อสะสมครบ 6 บรรทัด (ตัวอย่างคร่าว ๆ)
                if len(buffer) >= 6 and any(" - " in b for b in buffer):
                    awb_line = buffer.pop(0)
                    piece_line = buffer.pop(0)
                    weight_line = buffer.pop(0)
                    desc_line = buffer.pop(0)
                    shc_line = buffer.pop(0)
                    route_line = buffer.pop(0)

                    # ตัดแต่งข้อมูล
                    awb = awb_line.replace(" ", "").strip()
                    pieces = piece_line.split("/")[0]
                    piece_type = "P" if "/" in piece_line else "T"
                    weight = weight_line.split("/")[0].strip()
                    mc = round(float(weight) * 0.006, 2)
                    description = f"{desc_line.strip()} {shc_line.strip()}".strip()
                    route = route_line.replace(" ", "").replace("-", "").strip()
                    dest = route[-3:] if len(route) >= 6 else "XXX"

                    formatted = f"{awb}{route}/" \
                                f"{piece_type}{pieces}K{weight}MC{mc}" \
                                f"{'T'+piece_line.split('/')[-1] if '/' in piece_line else ''}" \
                                f"/{description}"

                    if "ULD/" in current_uld:
                        ffm_lines.append(formatted)
                    else:
                        current_uld = f"ULD/{desc_line.strip().replace(' ', '').upper()}"
                        ffm_lines.append(current_uld)
                        ffm_lines.append(formatted)

                    buffer.clear()

    return "\n".join(ffm_lines)
