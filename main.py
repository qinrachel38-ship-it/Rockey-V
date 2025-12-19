import logging
import uuid
from typing import Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Content Distribution Demo")


class Content(BaseModel):
    id: str = Field(..., description="Unique content identifier")
    filename: str = Field(..., description="Uploaded filename")
    status: str = Field(..., description="Current content status")


class ContentResponse(Content):
    pass


class DistributionIntent(BaseModel):
    id: str = Field(..., description="Unique distribution intent identifier")
    content_id: str = Field(..., description="Linked content identifier")
    platform: str = Field(..., description="Target distribution platform")
    status: str = Field(..., description="Current intent status")


class CreateIntentRequest(BaseModel):
    content_id: str
    platform: str


class IntentResponse(DistributionIntent):
    pass


# In-memory storage
contents: Dict[str, Content] = {}
intents: Dict[str, DistributionIntent] = {}


@app.post("/upload", response_model=ContentResponse)
async def upload(file: UploadFile = File(...)) -> ContentResponse:
    logger.info("Received upload request for file: %s", file.filename)
    content_id = str(uuid.uuid4())

    content = Content(id=content_id, filename=file.filename, status="uploading")
    contents[content_id] = content
    logger.info("Content %s status changed to %s", content_id, content.status)

    # Simulate processing to reach ready_for_distribution
    content.status = "ready_for_distribution"
    logger.info("Content %s status changed to %s", content_id, content.status)
    return ContentResponse(**content.dict())


@app.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str) -> ContentResponse:
    content = contents.get(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    logger.info("Fetched content %s with status %s", content_id, content.status)
    return ContentResponse(**content.dict())


@app.post("/intent", response_model=IntentResponse)
async def create_intent(request: CreateIntentRequest) -> IntentResponse:
    logger.info(
        "Received distribution intent request for content %s to platform %s",
        request.content_id,
        request.platform,
    )

    content = contents.get(request.content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found for intent")

    intent_id = str(uuid.uuid4())
    intent = DistributionIntent(
        id=intent_id,
        content_id=request.content_id,
        platform=request.platform,
        status="pending",
    )
    intents[intent_id] = intent
    logger.info("Intent %s created with status %s", intent_id, intent.status)
    return IntentResponse(**intent.dict())


@app.get("/intent/{intent_id}", response_model=IntentResponse)
async def get_intent(intent_id: str) -> IntentResponse:
    intent = intents.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    logger.info(
        "Fetched intent %s for content %s with status %s",
        intent_id,
        intent.content_id,
        intent.status,
    )
    return IntentResponse(**intent.dict())


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
