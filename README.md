# Pronunciation Mirror (Prototype) — Live Compare

- **Live Compare (beta):** while recording, the app continuously takes the last ~reference-length audio, computes envelope & pitch, overlays it against the reference, and updates the score about every 250–300ms.
- **Upload mode:** you can still upload a user attempt or stop the mic to compare a full take.
- **Optional MFA backend:** get word/phoneme boundaries for the reference (and extend to the user's attempt).

## Use
1) Open `frontend/index.html` in a modern browser.
2) Load a **reference** MP3/WAV (and optionally paste a transcript).
3) Toggle **Live compare (beta)** if you want near-realtime feedback.
4) Click **Start Mic** and repeat the phrase; watch overlay + score update live.
5) Click **Stop** any time to freeze and review; or **Compare & Score** for a one-shot take.
6) (Optional) Run backend and click **Align (MFA)** to draw word bars.

## Backend (optional)
Create a conda env, install MFA and models (e.g., Swedish), and run:
```
pip install -r backend/requirements.txt
conda install -c conda-forge montreal-forced-aligner -y
mfa model download acoustic swedish_mfa
mfa model download dictionary swedish_mfa
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Next improvements: 
Labels for each word/phoneme (the code currently only draws the boundary lines, not the text).
Alignment for your own attempt — right now it only aligns the reference audio to its transcript.
Constant reply of source audio enabling user to match (and enabling overlapping waves).
