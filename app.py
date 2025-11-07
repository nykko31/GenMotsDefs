import spacy
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Chargement du modèle FR
nlp = spacy.load("fr_core_news_md")

# ---------- MODELES ----------

class PairInput(BaseModel):
    word1: str
    word2: str

class BatchInput(BaseModel):
    word: str
    candidates: List[str]

class FilterInput(BaseModel):
    validated: List[str]
    candidates: List[str]
    threshold: float = 0.80   # limite similarité par défaut


# ---------- ENDPOINTS ----------

@app.post("/similarity")
def similarity(data: PairInput):
    v1 = nlp(data.word1)
    v2 = nlp(data.word2)
    return {"similarity": v1.similarity(v2)}


@app.post("/batch_similarity")
def batch_similarity(data: BatchInput):
    w = nlp(data.word)
    out = []
    for c in data.candidates:
        score = w.similarity(nlp(c))
        out.append({"candidate": c, "similarity": score})
    return out


@app.post("/filter_candidates")
def filter_candidates(data: FilterInput):
    """
    Retire les candidats trop proches de l’un des mots validés.
    """
    validated_vecs = [nlp(v) for v in data.validated]
    kept = []
    removed = []

    for c in data.candidates:
        vc = nlp(c)
        max_sim = max((vc.similarity(v) for v in validated_vecs), default=0.0)

        if max_sim >= data.threshold:
            removed.append({"mot": c, "similarity": max_sim})
        else:
            kept.append(c)

    return {
        "kept": kept,
        "removed": removed,
        "threshold": data.threshold
    }
