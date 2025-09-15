# Rockey-V
AI Transfer & Distribution of Video Contents

## Backend

Install dependencies and run the API server:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Endpoints

- `POST /upload` – upload an MP4, get back the saved path, Whisper transcript, a 3‑sentence summary, and 2‑3 marketing highlights.
- `POST /analyze` – upload a video file and receive transcription, summary, and marketing highlights.
- `POST /metadata` – send the summary and highlights to get platform-specific titles and tags.
- `POST /regenerate` – regenerate 3 titles and tags for YouTube, TikTok, and Instagram from a summary and highlights.
- `POST /publish` – append platform, video path, title, and tags to `published_log.json` to simulate publishing.
