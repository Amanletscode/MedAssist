import json

INPUT = "icd10_source.txt"
OUTPUT = "medical_codes/icd10.json"


def normalize(code):
    code = code.strip().upper()
    if len(code) > 3 and code[0].isalpha():
        return code[0] + code[1:3] + "." + code[3:]
    return code


def main():
    icd_map = {}
    
    with open(INPUT, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(None, 4)
            if len(parts) < 5:
                continue

            _, raw_code, level, short_desc, long_desc = parts[0], parts[1], parts[2], parts[3], parts[4]

            # Keep *only level==1* which are real billable diagnosis codes
            if level != "1":
                continue

            code = normalize(raw_code)
            desc = long_desc.strip()
            icd_map[code] = desc

    with open(OUTPUT, "w", encoding="utf-8") as out:
        json.dump(icd_map, out, ensure_ascii=False, indent=2)

    print("Saved:", OUTPUT)
    print("Total billable ICD-10-CM codes:", len(icd_map))


if __name__ == "__main__":
    main()
