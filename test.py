
from ffm_parser import parse_manifest_to_ffm8

# เปลี่ยน path ให้เป็นชื่อไฟล์ PDF ที่ต้องการ
pdf_path = "MNFT SU285 24MAY25.pdf"

output = parse_manifest_to_ffm8(pdf_path)
print(output)
