import csv, json

INPUT = "cpt4_source.csv"
OUTPUT = "medical_codes/cpt4.json"

def main():
    cpt_map = {}

    with open(INPUT, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            code = row[0].strip().upper()
            desc = row[1].strip()
            cpt_map[code] = desc

    with open(OUTPUT, "w", encoding="utf-8") as out:
        json.dump(cpt_map, out, indent=2, ensure_ascii=False)

    print("Saved:", OUTPUT)
    print("Total CPT codes:", len(cpt_map))

if __name__ == "__main__":
    main()
