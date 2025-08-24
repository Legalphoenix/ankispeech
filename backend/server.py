# FastAPI backend to wrap Montreal Forced Aligner (MFA) for alignment.
import os, tempfile, subprocess
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from textgrid import TextGrid

app = FastAPI(title="Pronunciation Mirror Backend (MFA)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def parse_textgrid(path:str):
    tg = TextGrid.fromFile(path)
    words, phones = [], []
    for tier in tg:
        name = (tier.name or "").lower()
        if "word" in name or name == "words":
            for it in tier:
                if getattr(it, "mark", "").strip():
                    words.append({"word": it.mark, "start": float(it.minTime), "end": float(it.maxTime)})
        if "phone" in name or "phoneme" in name or name == "phones":
            for it in tier:
                if getattr(it, "mark", "").strip():
                    phones.append({"phone": it.mark, "start": float(it.minTime), "end": float(it.maxTime)})
    return {"words": words, "phones": phones}

@app.post("/align")
async def align(audio: UploadFile = File(...), transcript: str = Form(...), language: str = Form("swedish")):
    '''
    Align an audio file + transcript using MFA.
    - audio: WAV/MP3/etc (wav recommended)
    - transcript: raw text
    - language: default 'swedish' – expects swedish_mfa models installed
    Returns JSON with word and phone boundaries.
    '''
    lang = (language or "swedish").lower()
    if lang == "swedish":
        dict_name = "swedish_mfa"; acoustic_name = "swedish_mfa"
    elif lang == "english":
        dict_name = "english_us_arpa"; acoustic_name = "english_us_mfa"
    else:
        dict_name = f"{lang}_mfa"; acoustic_name = f"{lang}_mfa"

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, audio.filename)
        with open(audio_path, "wb") as f: f.write(await audio.read())

        base = os.path.splitext(os.path.basename(audio_path))[0]
        lab_path = os.path.join(tmpdir, f"{base}.lab")
        with open(lab_path, "w", encoding="utf-8") as f: f.write(transcript.strip())

        out_dir = os.path.join(tmpdir, "aligned"); os.makedirs(out_dir, exist_ok=True)
        cmd = ["mfa", "align", tmpdir, dict_name, acoustic_name, out_dir, "--clean"]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        except subprocess.CalledProcessError as e:
            return JSONResponse(status_code=500, content={"error": "MFA failed", "stderr": e.stderr})

        tg_path = os.path.join(out_dir, f"{base}.TextGrid")
        if not os.path.exists(tg_path): return JSONResponse(status_code=500, content={"error": "No TextGrid produced by MFA"})
        return JSONResponse(content=parse_textgrid(tg_path))
