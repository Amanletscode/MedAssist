# embedding_engine.py
"""
Precompute local embeddings for ICD10 and CPT4 using sentence-transformers.
Run once:
    python embedding_engine.py

Outputs:
    medical_codes/icd10_embeddings.npy
    medical_codes/icd10_codes.json
    medical_codes/cpt4_embeddings.npy
    medical_codes/cpt4_codes.json
"""
from sentence_transformers import SentenceTransformer
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm

# Paths
ICD_PATH = Path("medical_codes/icd10.json")
CPT_PATH = Path("medical_codes/cpt4.json")
OUT_DIR = Path("medical_codes")
OUT_DIR.mkdir(exist_ok=True)

# Model
# MODEL_NAME = "all-MiniLM-L6-v2"  
MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"
BATCH_SIZE = 512  # safe on 8GB RAM

def load_descriptions(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    # data is a dict {code: description}
    codes = list(data.keys()) 
    descriptions = [f"{code} {data[code]}" if data[code] else f"{code}" for code in codes]
    return codes, descriptions

def embed_and_save(codes, descriptions, out_npy: Path, out_codes: Path):
    model = SentenceTransformer(MODEL_NAME)
    embeddings = []
    for i in tqdm(range(0, len(descriptions), BATCH_SIZE), desc="Embedding batches"):
        batch = descriptions[i:i+BATCH_SIZE]
        emb = model.encode(batch, show_progress_bar=False, convert_to_numpy=True)
        embeddings.append(emb)
    embeddings = np.vstack(embeddings)
    # L2 normalize embeddings for cosine similarity via dot product
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms==0] = 1.0
    embeddings = embeddings / norms
    np.save(out_npy, embeddings)
    out_codes.write_text(json.dumps(codes, ensure_ascii=False), encoding="utf-8")
    print(f"Saved embeddings shape {embeddings.shape} to {out_npy}")
    print(f"Saved codes list to {out_codes}")

def main():
    if not ICD_PATH.exists() or not CPT_PATH.exists():
        raise FileNotFoundError("ICD/CPT json files missing. Put medical_codes/icd10.json and cpt4.json in place.")
    icd_codes, icd_desc = load_descriptions(ICD_PATH)
    cpt_codes, cpt_desc = load_descriptions(CPT_PATH)

    print("Embedding ICD-10 descriptions...")
    embed_and_save(icd_codes, icd_desc, OUT_DIR / "icd10_embeddings.npy", OUT_DIR / "icd10_codes.json")

    print("Embedding CPT-4 descriptions...")
    embed_and_save(cpt_codes, cpt_desc, OUT_DIR / "cpt4_embeddings.npy", OUT_DIR / "cpt4_codes.json")

if __name__ == "__main__":
    main()
