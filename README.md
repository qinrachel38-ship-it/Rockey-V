# Rockey-V

AI Transfer & Distribution of Video Contents

## Demo overview
A minimal FastAPI backend demonstrating an upload-to-distribution flow using in-memory storage and verbose logging.

### Core data structures
- **Content**: tracks uploaded video metadata and status transitions to `ready_for_distribution`.
- **DistributionIntent**: represents a user's choice to distribute content to a platform with initial status `pending`.

### API endpoints
- `POST /upload`: upload a video file, returns `content_id` and content status.
- `GET /content/{id}`: fetch content details.
- `POST /intent`: create a distribution intent for a content ID and target platform.
- `GET /intent/{id}`: fetch intent details.
- `GET /health`: simple health check.

### Running the demo
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `uvicorn main:app --reload`
3. Example requests (using `httpie`):
   ```bash
   http -f POST :8000/upload file@/path/to/video.mp4
   http POST :8000/intent content_id==<content_id> platform==YouTube
   http GET :8000/content/<content_id>
   http GET :8000/intent/<intent_id>
   ```

All state is stored in memory and resets when the server restarts. Logging prints every status change and retrieval for clarity.
