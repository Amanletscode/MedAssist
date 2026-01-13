"""
convert_codes.py

Usage:
  Put the original large files (ICD10.json and CPT4.json from MediSuite or other source)
  into the project folder (or specify paths below) and run:

    python convert_codes.py

It will produce optimized dictionary JSONs in medical_codes/icd10.json and medical_codes/cpt4.json
"""

import json
import re
from pathlib import Path
from html import unescape

# ---- CONFIG: paths to your original files ----
# If your original files have different names/locations, update these.
RAW_ICD_PATH = Path("ICD10.json")        # original raw file (from MediSuite)
RAW_CPT_PATH = Path("CPT4.json")         # original raw file (from MediSuite)

OUT_DIR = Path("medical_codes")
OUT_DIR.mkdir(exist_ok=True)

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    # Unescape HTML entities, remove extra whitespace, normalize quotes
    s = unescape(str(s))
    s = s.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s

def try_load_json(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception as e:
        print(f"Error parsing JSON {path}: {e}")
        raise

def format_icd_code(code: str) -> str:
    """
    Format ICD-10 code with proper dot placement.
    E.g., 'A0100' -> 'A01.00', 'A001' -> 'A00.1', 'R509' -> 'R50.9'
    """
    code = code.strip().upper()
    # If already has a dot, return as-is
    if '.' in code:
        return code
    # ICD-10 codes have dot after 3rd character
    if len(code) > 3:
        return code[:3] + '.' + code[3:]
    return code


def convert_icd(raw) -> dict:
    """
    Convert various raw shapes to { code: description } mapping.
    raw can be:
      - list of dicts each with keys like "code", "disease", "category"
      - list of dicts with different field names
      - dict already mapping code->desc
    
    IMPORTANT: Prioritize 'disease' field over 'category' for full descriptions.
    """
    out = {}
    if isinstance(raw, dict):
        # maybe already mapping
        for k, v in raw.items():
            formatted_code = format_icd_code(str(k))
            out[formatted_code] = normalize_text(v)
        return out

    if isinstance(raw, list):
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            
            code = None
            desc = None
            
            # Extract code
            for key in ("code", "Code", "CODE", "icd_code", "icd10"):
                if key in entry and entry[key]:
                    code = entry[key]
                    break
            
            # PRIORITY ORDER for description: disease > description > desc > name > term
            # DO NOT use 'category' as primary - it's often just a partial label
            for key in ("disease", "disease_name", "diseaseDescription", "description", "desc", "name", "term"):
                if key in entry and entry[key]:
                    desc = entry[key]
                    break
            
            # If no description found, try category as last resort
            if not desc and "category" in entry and entry["category"]:
                desc = entry["category"]
            
            # Fallback: find code-like value
            if not code and len(entry) >= 1:
                for v in entry.values():
                    if isinstance(v, str) and re.match(r"^[A-Z0-9\.]+$", v.strip(), re.I):
                        code = v
                        break
            
            # Fallback: find longest string as description
            if not desc:
                strings = [str(v) for v in entry.values() if isinstance(v, str)]
                strings = sorted(strings, key=lambda x: len(x), reverse=True)
                if strings:
                    desc = strings[0]
            
            if code:
                formatted_code = format_icd_code(str(code))
                desc = normalize_text(desc) if desc else ""
                out[formatted_code] = desc
    return out

def convert_cpt(raw) -> dict:
    """
    Similar logic for CPT: try to get code and procedure description
    """
    out = {}
    if isinstance(raw, dict):
        for k, v in raw.items():
            out[str(k).strip().upper()] = normalize_text(v)
        return out

    if isinstance(raw, list):
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            code = None
            desc = None
            for key in ("code", "procedure", "Procedure", "proc", "CPT4", "cpt"):
                if key in entry and entry[key]:
                    # heuristics: if the key looks like code or desc
                    if key.lower() in ("code", "cpt", "cpt4"):
                        code = entry[key]
                    else:
                        # sometimes procedure stored under 'procedure'
                        desc = entry[key]
            # fallback heuristics
            if not code:
                # find value that matches typical CPT pattern (digits, maybe leading zeros)
                for v in entry.values():
                    if isinstance(v, str) and re.match(r"^\d{3,6}[A-Z]?$", v.strip()):
                        code = v
                        break
            if not desc:
                strings = [str(v) for v in entry.values() if isinstance(v, str)]
                strings = sorted(strings, key=lambda x: len(x), reverse=True)
                if strings:
                    # prefer those strings that are not pure digits
                    for s in strings:
                        if not re.match(r"^\d+$", s.strip()):
                            desc = s
                            break
                    if not desc:
                        desc = strings[0]
            if code:
                code = str(code).strip().upper()
                out[code] = normalize_text(desc) if desc else ""
    return out

def save_json(path: Path, data: dict):
    print(f"Saving {len(data):,} entries to {path}")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    # ICD
    if RAW_ICD_PATH.exists():
        raw = try_load_json(RAW_ICD_PATH)
        icd_map = convert_icd(raw)
        save_json(OUT_DIR / "icd10.json", icd_map)
    else:
        print(f"Warning: {RAW_ICD_PATH} not found. Skipping ICD conversion.")

    # CPT
    if RAW_CPT_PATH.exists():
        raw = try_load_json(RAW_CPT_PATH)
        cpt_map = convert_cpt(raw)
        save_json(OUT_DIR / "cpt4.json", cpt_map)
    else:
        print(f"Warning: {RAW_CPT_PATH} not found. Skipping CPT conversion.")

    print("Conversion complete. Verify the files in 'medical_codes' folder.")

if __name__ == "__main__":
    main()
