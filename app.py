from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import spacy

app = FastAPI()

# Charger le modèle une fois au démarrage
try:
    nlp = spacy.load("fr_core_news_md")
except Exception as e:
    raise RuntimeError(f"Erreur de chargement Spacy : {e}")

# ----------- HEALTHCHECK -----------
@app.get("/health")
def health():
    return {"status": "ok"}


# ----------- MODELES Pydantic -----------

class PairInput(BaseModel):
    word1: str = Field(..., description="Premier mot")
    word2: str = Field(..., description="Second mot")

class BatchInput(BaseModel):
    pairs: list[PairInput] = Field(..., description="Liste de couples de mots")

class FilterInput(BaseModel):
    word: str
    candidates: list[str]


# ----------- SIMILARITÉ (GET + POST) -----------

@app.get("/similarity")
def similarity_get(word1: str, word2: str):
    try:
        score = nlp(word1).similarity(nlp(word2))
        return {"word1": word1, "word2": word2, "similarity": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similarity")
def similarity_post(data: PairInput):
    try:
        score = nlp(data.word1).similarity(nlp(data.word2))
        return {"word1": data.word1, "word2": data.word2, "similarity": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------- BATCH SIMILARITY -----------

@app.post("/batch_similarity")
def batch_similarity(data: BatchInput):
    try:
        results = []
        for pair in data.pairs:
            score = nlp(pair.word1).similarity(nlp(pair.word2))
            results.append({
                "word1": pair.word1,
                "word2": pair.word2,
                "similarity": score
            })
        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------- FILTRAGE DE CANDIDATS -----------

@app.post("/filter_candidates")
def filter_candidates(data: FilterInput):
    try:
        target = nlp(data.word)
        output = []

        for cand in data.candidates:
            sim = target.similarity(nlp(cand))
            output.append({"candidate": cand, "similarity": sim})

        output = sorted(output, key=lambda x: x["similarity"], reverse=True)

        return {"word": data.word, "ranked_candidates": output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
