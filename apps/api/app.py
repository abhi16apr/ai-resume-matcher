from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np
import io
from pdfminer.high_level import extract_text as pdf_to_text
import docx

app = Flask(__name__)
CORS(app)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed(text: str) -> np.ndarray:
    v = model.encode([text], normalize_embeddings=True)
    return v.astype("float32")

def docx_to_text(file_bytes: bytes) -> str:
    f = io.BytesIO(file_bytes)
    d = docx.Document(f)
    return "\n".join([p.text for p in d.paragraphs])

def extract_resume_text(upload) -> str:
    name = upload.filename.lower()
    data = upload.read()
    if name.endswith(".pdf"):
        return pdf_to_text(io.BytesIO(data))
    if name.endswith(".docx"):
        return docx_to_text(data)
    try:
        return data.decode("utf-8", errors="ignore")
    except:
        return ""

KEYWORDS = {
    "python","java","javascript","typescript","react","next.js","node","express",
    "aws","gcp","azure","sql","postgres","mysql","mongodb","docker","kubernetes",
    "tensorflow","pytorch","langchain","llm","nlp","rest","graphql","ci/cd"
}

def skills_from_text(t: str) -> list[str]:
    tl = t.lower()
    return sorted({k for k in KEYWORDS if k in tl})

def score_similarity(resume_txt: str, jd_txt: str) -> dict:
    r = embed(resume_txt)
    j = embed(jd_txt)
    sim = float(np.dot(r, j.T)[0][0])
    score = round(50 + 50*sim, 1)

    resume_sk = set(skills_from_text(resume_txt))
    jd_sk     = set(skills_from_text(jd_txt))
    overlap   = sorted(resume_sk & jd_sk)
    gaps      = sorted(jd_sk - resume_sk)
    recs = [f"Add a bullet showing impact with {g} (project, metrics, outcome)." for g in gaps]
    return {"score": score, "overlap": overlap, "gaps": gaps, "recommendations": recs}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/match")
def match():
    job_text = request.form.get("job_text", "").strip()
    if not job_text:
        return jsonify({"error": "job_text required"}), 400

    resume_text = request.form.get("resume_text", "").strip()
    if "resume" in request.files and request.files["resume"].filename:
        resume_text = extract_resume_text(request.files["resume"])

    if not resume_text:
        return jsonify({"error": "resume_text or resume file required"}), 400

    result = score_similarity(resume_text, job_text)
    return jsonify({"ok": True, **result})

if __name__ == "__main__":
    app.run(port=8000, debug=True)

@app.get("/")
def root():
    return {"ok": True, "endpoints": ["/health", "/match"]}
