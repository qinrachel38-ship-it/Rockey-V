import json
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import openai
from openai import OpenAI

app = FastAPI()
client = OpenAI()


class SummaryRequest(BaseModel):
    summary: str
    highlights: list[str]


class PublishRequest(BaseModel):
    platform: str
    video_path: str
    title: str
    tags: list[str]


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Save an uploaded MP4 video, transcribe it, and generate a summary and highlights."""
    if file.content_type != "video/mp4":
        raise HTTPException(status_code=400, detail="Invalid file type")
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe the saved video using OpenAI Whisper
    with open(file_path, "rb") as f:
        transcript = openai.Audio.transcriptions.create(model="whisper-1", file=f)
    text = transcript["text"]
    # Generate a 3-sentence summary and 2-3 highlights with GPT
    prompt = (
        f"请将以下转写内容总结为 3 句话，并提炼 2-3 个运营亮点，"
        f"以 JSON 格式返回，包含 'summary' 和 'highlights' 字段：\n\n{text}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    gpt_content = response["choices"][0]["message"]["content"]
    try:
        summary_data = json.loads(gpt_content)
    except json.JSONDecodeError:
        summary_data = {"summary": gpt_content.strip(), "highlights": []}

    return {
        "video_path": file_path,
        "transcript": text,
        "summary": summary_data.get("summary", ""),
        "highlights": summary_data.get("highlights", []),
    }


@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """Upload a video and get transcription, summary, and marketing highlights."""
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=file.file
    )
    transcription_text = transcription.text

    prompt = (
        "Summarize the following transcript and extract key marketing highlights.\n"
        "Return JSON with fields 'summary' and 'highlights' (list of strings).\n"
        f"{transcription_text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    result = json.loads(response.choices[0].message.content)

    return {
        "transcription": transcription_text,
        "summary": result.get("summary", ""),
        "highlights": result.get("highlights", []),
    }


@app.post("/metadata")
async def generate_metadata(req: SummaryRequest):
    """Generate titles and tags for YouTube, TikTok, and Instagram."""
    prompt = (
        "Given the following summary and marketing highlights, generate catchy titles"
        " and a list of tags for YouTube, TikTok, and Instagram. Return JSON with"
        " keys 'youtube', 'tiktok', and 'instagram', each containing 'title' and"
        " 'tags' (list).\n"
        f"Summary: {req.summary}\n"
        f"Highlights: {req.highlights}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    metadata = json.loads(response.choices[0].message.content)

    return metadata


@app.post("/regenerate")
async def regenerate_titles(req: SummaryRequest):
    """Regenerate platform-specific titles and tags from summary and highlights."""
    prompt = (
        f"基于以下摘要和亮点，为 YouTube、TikTok 和 Instagram 生成 3 个标题和对应标签。\n"
        f"摘要: {req.summary}\n"
        f"亮点: {req.highlights}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一名资深的社交媒体运营顾问。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=800,
    )
    try:
        content = response["choices"][0]["message"]["content"]
        metadata = json.loads(content)
    except (KeyError, json.JSONDecodeError):
        metadata = {
            "YouTube": {"titles": [], "tags": []},
            "TikTok": {"titles": [], "tags": []},
            "Instagram": {"titles": [], "tags": []},
        }
    return metadata


@app.post("/publish")
async def publish_content(req: PublishRequest):
    """Simulate publishing by appending data to a local JSON log file."""
    log_entry = req.dict()
    log_file = "published_log.json"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    else:
        log = []
    log.append(log_entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    return {"status": "success", "saved_to": log_file}
