# ffm_parser.py
import pdfplumber

def parse_manifest_to_ffm8(pdf_path):
    ffm_lines = []
    bulk_entries = []
    uld_entries = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue
            for row in table[1:]:  # skip header
                if len(row) < 6:
                    continue
                awb, pcs, weight, dest, flight, uld = [cell.strip() if cell else '' for cell in row[:6]]

                if not awb or not pcs or not weight:
                    continue

                line = f"{awb} {pcs}K {weight}K {dest}"

                if uld.upper().startswith("BULK"):
                    bulk_entries.append("BULK/" + line)
                elif uld:
                    uld_entries.append(f"ULD/{uld.upper()}\n{line}")
                else:
                    bulk_entries.append("BULK/" + line)

    # Combine lines with BULK first, then ULD
    ffm_lines.extend(bulk_entries)
    ffm_lines.extend(uld_entries)

    return "FFM/8\n" + "\n".join(ffm_lines)
