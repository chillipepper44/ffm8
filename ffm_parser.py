# ffm_parser.py
import fitz  # PyMuPDF

def parse_manifest_to_ffm8(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    lines = []
    current_uld = None

    for page in doc:
        text = page.get_text("text")
        blocks = text.split("\n")

        i = 0
        while i < len(blocks):
            line = blocks[i].strip()

            # ตรวจจับ ULD
            if line.startswith("ULD/") or (
                len(line) == 11 and line[:3].isalpha() and line[3:].isdigit()
            ):
                current_uld = f"ULD/{line}"
                if current_uld not in lines:
                    lines.append(current_uld)
                i += 1
                continue

            # ตรวจจับ AWB
            if line[:3].isdigit() and " - " in line:
                try:
                    awb = line.replace(" ", "")
                    pieces_line = blocks[i + 1].strip()
                    weight_line = blocks[i + 2].strip()
                    desc_line = blocks[i + 3].strip()
                    shc_line = blocks[i + 4].strip()
                    route_line = blocks[i + 5].strip()

                    # สร้าง prefix S = part, T = total
                    pieces = pieces_line.split()[0]
                    piece_type = "S" if "/" in pieces else "T"
                    piece_value = pieces.split("/")[0] if "/" in pieces else pieces

                    weight = weight_line.split("/")[0].strip()
                    weight_value = float(weight)
                    weight_str = f"{weight_value:.2f}".rstrip("0").rstrip(".")
                    mc = round(weight_value * 0.006, 2)
                    mc_str = f"{mc:.2f}".rstrip("0").rstrip(".")

                    desc = f"{desc_line} {shc_line}".strip()
                    route = route_line.replace(" ", "").replace("-", "")
                    if len(route) >= 6:
                        org = route[:3]
                        dest = route[-3:]
                        route_str = f"{org}{dest}"
                    else:
                        route_str = "XXXXXX"

                    formatted = (
                        f"{awb}{route_str}/{piece_type}{piece_value}K{weight_str}MC{mc_str}T"
                    )

                    # ดึง Txx หากมีจาก pieces
                    if "/" in pieces_line:
                        t_part = pieces_line.split("/")[1]
                        formatted += f"{t_part}"

                    if desc:
                        formatted += f"/{desc}"

                    lines.append(formatted)
                    i += 6
                except Exception:
                    i += 1
                    continue
            else:
                i += 1

    doc.close()
    return "FFM/8\n" + "\n".join(lines)
