# semantic_search.py
"""
Semantic search for medical codes using pre-computed embeddings.

This module provides fast similarity search over ICD-10 and CPT-4 codes
using cosine similarity with normalized embeddings.
"""
import numpy as np
import json
from pathlib import Path
from typing import List, Tuple, Optional

OUT_DIR = Path("medical_codes")
ICD_EMB = OUT_DIR / "icd10_embeddings.npy"
ICD_CODES = OUT_DIR / "icd10_codes.json"
CPT_EMB = OUT_DIR / "cpt4_embeddings.npy"
CPT_CODES = OUT_DIR / "cpt4_codes.json"

# Lazy-loaded globals
_model = None
_icd_emb: Optional[np.ndarray] = None
_icd_codes: Optional[List[str]] = None
_cpt_emb: Optional[np.ndarray] = None
_cpt_codes: Optional[List[str]] = None

# Clinical BERT model - good for medical terminology
MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"


class EmbeddingError(Exception):
    """Raised when embedding operations fail."""
    pass


def _ensure_model():
    """Load the sentence transformer model (lazy initialization)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME)
        except ImportError:
            raise EmbeddingError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
        except Exception as e:
            raise EmbeddingError(f"Failed to load model '{MODEL_NAME}': {e}")
    return _model


def _load_icd() -> Tuple[np.ndarray, List[str]]:
    """Load ICD-10 embeddings and codes."""
    global _icd_emb, _icd_codes
    if _icd_emb is None:
        if not ICD_EMB.exists():
            raise EmbeddingError(
                f"ICD embeddings not found at {ICD_EMB}. "
                "Run: python embedding_engine.py"
            )
        if not ICD_CODES.exists():
            raise EmbeddingError(
                f"ICD codes not found at {ICD_CODES}. "
                "Run: python embedding_engine.py"
            )
        try:
            _icd_emb = np.load(ICD_EMB)
            _icd_codes = json.loads(ICD_CODES.read_text(encoding="utf-8"))
        except Exception as e:
            raise EmbeddingError(f"Failed to load ICD data: {e}")
        
        if len(_icd_codes) != _icd_emb.shape[0]:
            raise EmbeddingError(
                f"Mismatch: {len(_icd_codes)} codes vs {_icd_emb.shape[0]} embeddings. "
                "Regenerate embeddings with: python embedding_engine.py"
            )
    return _icd_emb, _icd_codes


def _load_cpt() -> Tuple[np.ndarray, List[str]]:
    """Load CPT-4 embeddings and codes."""
    global _cpt_emb, _cpt_codes
    if _cpt_emb is None:
        if not CPT_EMB.exists():
            raise EmbeddingError(
                f"CPT embeddings not found at {CPT_EMB}. "
                "Run: python embedding_engine.py"
            )
        if not CPT_CODES.exists():
            raise EmbeddingError(
                f"CPT codes not found at {CPT_CODES}. "
                "Run: python embedding_engine.py"
            )
        try:
            _cpt_emb = np.load(CPT_EMB)
            _cpt_codes = json.loads(CPT_CODES.read_text(encoding="utf-8"))
        except Exception as e:
            raise EmbeddingError(f"Failed to load CPT data: {e}")
        
        if len(_cpt_codes) != _cpt_emb.shape[0]:
            raise EmbeddingError(
                f"Mismatch: {len(_cpt_codes)} codes vs {_cpt_emb.shape[0]} embeddings. "
                "Regenerate embeddings with: python embedding_engine.py"
            )
    return _cpt_emb, _cpt_codes


def _embed_query(text: str) -> np.ndarray:
    """
    Embed a query text and return normalized vector.
    
    Args:
        text: The query string to embed
        
    Returns:
        Normalized embedding vector
    """
    if not text or not text.strip():
        raise EmbeddingError("Cannot embed empty query")
    
    model = _ensure_model()
    vec = model.encode([text], convert_to_numpy=True)[0]
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


def semantic_search_icd(query: str, top_k: int = 10) -> List[Tuple[str, float]]:
    """
    Search for ICD-10 codes semantically similar to the query.
    
    Args:
        query: Clinical description to search for
        top_k: Number of results to return
        
    Returns:
        List of (code, similarity_score) tuples, sorted by score descending
    """
    emb, codes = _load_icd()
    qv = _embed_query(query)
    
    # Cosine similarity via dot product (embeddings are pre-normalized)
    scores = emb.dot(qv)
    
    # Get top-k indices efficiently
    k = min(top_k, len(scores))
    if k <= 0:
        return []
    
    # Use argpartition for efficiency on large arrays
    idx = np.argpartition(-scores, range(k))[:k]
    idx_sorted = idx[np.argsort(-scores[idx])]
    
    results = [(codes[i], float(scores[i])) for i in idx_sorted]
    return results


def semantic_search_cpt(query: str, top_k: int = 10) -> List[Tuple[str, float]]:
    """
    Search for CPT-4 codes semantically similar to the query.
    
    Args:
        query: Procedure description to search for
        top_k: Number of results to return
        
    Returns:
        List of (code, similarity_score) tuples, sorted by score descending
    """
    emb, codes = _load_cpt()
    qv = _embed_query(query)
    
    scores = emb.dot(qv)
    
    k = min(top_k, len(scores))
    if k <= 0:
        return []
    
    idx = np.argpartition(-scores, range(k))[:k]
    idx_sorted = idx[np.argsort(-scores[idx])]
    
    results = [(codes[i], float(scores[i])) for i in idx_sorted]
    return results


def clear_cache():
    """Clear cached embeddings and model (useful for testing or memory management)."""
    global _model, _icd_emb, _icd_codes, _cpt_emb, _cpt_codes
    _model = None
    _icd_emb = None
    _icd_codes = None
    _cpt_emb = None
    _cpt_codes = None
