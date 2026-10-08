from pathlib import Path
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from app.db import record_processing
from app.services.measurement import GeospatialProcessingError, process_file

router = APIRouter(tags=["measurement"])


@router.post("/measure")
async def measure(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Unsupported file type.")

    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(413, "File exceeds the maximum upload size.")

    try:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / filename
            path.write_bytes(data)
            result = process_file(path)
        record_processing(filename, len(data), result["feature_count"], "success")
        return {"filename": filename, **result}
    except GeospatialProcessingError as exc:
        record_processing(filename, len(data), 0, "failed")
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        record_processing(filename, len(data), 0, "failed")
        raise HTTPException(422, f"Unable to process geospatial file: {exc}") from exc
