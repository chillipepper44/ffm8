from ffm_parser import parse_manifest_to_ffm8

with open("MNFT SU285 24MAY25.pdf", "rb") as f:
    result = parse_manifest_to_ffm8(f)

print(result)
