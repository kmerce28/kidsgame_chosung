from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import io
import numpy as np
import soundfile as sf
import librosa

from konlpy.tag import Kkma

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHOSEONG_LIST = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


def normalize(word: str) -> str:
    if not word:
        return ''
    return ''.join(ch for ch in word.strip() if 0xAC00 <= ord(ch) <= 0xD7A3)


def get_initials(word: str) -> str:
    initials = []
    for ch in word:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            syllable_index = code - 0xAC00
            choseong_index = syllable_index // 588
            if 0 <= choseong_index < len(CHOSEONG_LIST):
                initials.append(CHOSEONG_LIST[choseong_index])
    return ''.join(initials)


kkma = Kkma()


class ValidateRequest(BaseModel):
    word: str
    pattern: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/validate")
def validate(req: ValidateRequest):
    w = normalize(req.word)
    if not w:
        return {"ok": False, "reason": "not_hangul"}

    initials = get_initials(w)
    if not initials.startswith(req.pattern):
        return {"ok": False, "reason": "initials_mismatch"}

    try:
        nouns = kkma.nouns(w)
    except Exception as e:
        return {"ok": False, "reason": "kkma_error"}

    ok = (w in nouns) or any(n == w for n in nouns)
    return {"ok": ok, "reason": "ok" if ok else "not_noun"}


# ----------------------------
# Total score storage (simple JSON)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOTAL_SCORES_PATH = os.path.join(BASE_DIR, 'total_scores.json')
SPEAKER_DB_PATH = os.path.join(BASE_DIR, 'speaker_db.json')


def load_json(path: str, default):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(path: str, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


@app.get('/total-scores')
def total_scores():
    scores = load_json(TOTAL_SCORES_PATH, {})
    return {"scores": scores}


class UpdateTotalScoresRequest(BaseModel):
    scores: dict


@app.post('/update-total-scores')
def update_total_scores(req: UpdateTotalScoresRequest):
    scores = load_json(TOTAL_SCORES_PATH, {})
    for name, inc in req.scores.items():
        scores[name] = scores.get(name, 0) + int(inc)
    save_json(TOTAL_SCORES_PATH, scores)
    return {"ok": True, "scores": scores}


# ----------------------------
# Speaker identification (simple MFCC centroid + cosine similarity)
# ----------------------------
def compute_embedding_from_wav_bytes(wav_bytes: bytes) -> np.ndarray:
    # Read audio
    data, sr = sf.read(io.BytesIO(wav_bytes))
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    target_sr = 16000
    if sr != target_sr:
        data = librosa.resample(y=data.astype(np.float32), orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    # MFCCs
    mfcc = librosa.feature.mfcc(y=data.astype(np.float32), sr=sr, n_mfcc=40)
    emb = np.mean(mfcc, axis=1)
    # L2 normalize
    norm = np.linalg.norm(emb) + 1e-8
    return emb / norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


@app.post('/speaker/register')
async def speaker_register(name: str = Form(...), audio: UploadFile = File(...)):
    wav_bytes = await audio.read()
    emb = compute_embedding_from_wav_bytes(wav_bytes)
    db = load_json(SPEAKER_DB_PATH, {})
    if name in db:
        # average embeddings if already exists
        old = np.array(db[name], dtype=np.float32)
        new = (old + emb) / 2.0
        db[name] = new.tolist()
    else:
        db[name] = emb.tolist()
    save_json(SPEAKER_DB_PATH, db)
    return {"ok": True}


@app.post('/speaker/identify')
async def speaker_identify(audio: UploadFile = File(...), threshold: float = 0.60):
    wav_bytes = await audio.read()
    emb = compute_embedding_from_wav_bytes(wav_bytes)
    db = load_json(SPEAKER_DB_PATH, {})
    if not db:
        return {"ok": False, "reason": "no_speakers"}
    best_name = None
    best_score = -1.0
    for name, vec in db.items():
        v = np.array(vec, dtype=np.float32)
        score = cosine_similarity(emb, v)
        if score > best_score:
            best_score = score
            best_name = name
    if best_score >= threshold:
        return {"ok": True, "name": best_name, "score": best_score}
    return {"ok": False, "reason": "below_threshold", "score": best_score}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
