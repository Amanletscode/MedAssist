# workflow.py
import json
from pathlib import Path

# semantic search
from semantic_search import semantic_search_icd, semantic_search_cpt

# fuzzy fallback
try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    _FWD = "rapidfuzz"
except Exception:
    try:
        from fuzzywuzzy import process as rf_process, fuzz as rf_fuzz
        _FWD = "fuzzywuzzy"
    except Exception:
        raise ImportError("Install rapidfuzz or fuzzywuzzy: pip install rapidfuzz")

# load maps
ICD_PATH = Path("medical_codes/icd10.json")
CPT_PATH = Path("medical_codes/cpt4.json")

def load_map(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run convert_codes.py or ensure file exists.")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

ICD_MAP = load_map(ICD_PATH)
CPT_MAP = load_map(CPT_PATH)

ICD_KEYS = list(ICD_MAP.keys())
ICD_SEARCH = [f"{k} {ICD_MAP[k]}" for k in ICD_KEYS]

CPT_KEYS = list(CPT_MAP.keys())
CPT_SEARCH = [f"{k} {CPT_MAP[k]}" for k in CPT_KEYS]


def fuzzy_suggest_icd(query: str, limit: int = 5):
    if not query.strip():
        return []
    results = rf_process.extract(query, ICD_SEARCH, limit=limit, scorer=rf_fuzz.WRatio)
    out = []
    for item in results:
        if _FWD == "rapidfuzz":
            match_str, score, idx = item
        else:
            match_str, score = item
            idx = ICD_SEARCH.index(match_str)
        code = ICD_KEYS[idx]
        out.append((code, ICD_MAP[code], int(score)))
    return out

def fuzzy_suggest_cpt(query: str, limit: int = 5):
    if not query.strip():
        return []
    results = rf_process.extract(query, CPT_SEARCH, limit=limit, scorer=rf_fuzz.WRatio)
    out = []
    for item in results:
        if _FWD == "rapidfuzz":
            match_str, score, idx = item
        else:
            match_str, score = item
            idx = CPT_SEARCH.index(match_str)
        code = CPT_KEYS[idx]
        out.append((code, CPT_MAP[code], int(score)))
    return out

def semantic_suggest_icd(query: str, top_k: int = 8):
    # returns (code, description, score) with score in [0,1]
    results = semantic_search_icd(query, top_k)
    return [(code, ICD_MAP.get(code, ""), round(score, 3)) for code, score in results]

def semantic_suggest_cpt(query: str, top_k: int = 8):
    results = semantic_search_cpt(query, top_k)
    return [(code, CPT_MAP.get(code, ""), round(score, 3)) for code, score in results]

# Semantic search thresholds (cosine similarity scores are 0.0 to 1.0)
# Below these thresholds, we augment with fuzzy search results
SEMANTIC_THRESHOLD_ICD = 0.35  # Minimum acceptable semantic similarity for ICD codes
SEMANTIC_THRESHOLD_CPT = 0.35  # Minimum acceptable semantic similarity for CPT codes


def suggest_icd10(query: str, limit: int = 5, method: str = "hybrid"):
    """
    Suggest ICD-10 codes for a given clinical query.
    
    method: 'semantic', 'fuzzy', 'hybrid'
    - semantic: Uses embedding-based similarity search
    - fuzzy: Uses string matching (rapidfuzz/fuzzywuzzy)  
    - hybrid: Combines both - semantic first, fuzzy for low-confidence results
    """
    if not query or not query.strip():
        return []
    
    if method == "semantic":
        return semantic_suggest_icd(query, top_k=limit)
    if method == "fuzzy":
        return fuzzy_suggest_icd(query, limit=limit)
    
    # Hybrid approach: semantic first, augment with fuzzy if needed
    sem = semantic_suggest_icd(query, top_k=limit * 2)  # Get more candidates
    
    # If semantic results are empty or top score is below threshold, add fuzzy
    top_score = sem[0][2] if sem else 0
    if not sem or top_score < SEMANTIC_THRESHOLD_ICD:
        fuzzy = fuzzy_suggest_icd(query, limit=limit)
        # Combine unique results, preserving order: semantic first
        seen = set()
        out = []
        for t in sem + fuzzy:
            if t[0] not in seen:
                seen.add(t[0])
                out.append(t)
            if len(out) >= limit:
                break
        return out[:limit]
    
    return sem[:limit]


def suggest_cpt(query: str, limit: int = 5, method: str = "hybrid"):
    """
    Suggest CPT-4 codes for a given procedure/clinical query.
    
    method: 'semantic', 'fuzzy', 'hybrid'
    """
    if not query or not query.strip():
        return []
    
    if method == "semantic":
        return semantic_suggest_cpt(query, top_k=limit)
    if method == "fuzzy":
        return fuzzy_suggest_cpt(query, limit=limit)
    
    # Hybrid approach
    sem = semantic_suggest_cpt(query, top_k=limit * 2)
    
    top_score = sem[0][2] if sem else 0
    if not sem or top_score < SEMANTIC_THRESHOLD_CPT:
        fuzzy = fuzzy_suggest_cpt(query, limit=limit)
        seen = set()
        out = []
        for t in sem + fuzzy:
            if t[0] not in seen:
                seen.add(t[0])
                out.append(t)
            if len(out) >= limit:
                break
        return out[:limit]
    
    return sem[:limit]
