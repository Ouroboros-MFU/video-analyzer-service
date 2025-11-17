import os
import time
import tempfile

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .database import Base, engine, get_db
from .models import AnalysisResult
from .schemas import AnalysisResultOut
from .video_analyzer import detect_motion
from .metrics import (
    videos_processed_total,
    videos_processing_errors_total,
    videos_processing_time_seconds,
)

app = FastAPI(title="Video Analyzer Service")


@app.on_event("startup")
def on_startup():
    # в прототипе создаём таблицы при старте, на проде c помощью миграции Alembic
    Base.metadata.create_all(bind=engine)


@app.post("/analyze", response_model=AnalysisResultOut)
async def analyze_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    start_time = time.monotonic()
    filename = file.filename or "uploaded_video"

    # сохраняем во временный файл, чтобы OpenCV смог прочитать
    try:
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name
    except Exception as e:
        videos_processing_errors_total.inc()
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    has_motion = False
    error_message = None

    try:
        has_motion = detect_motion(temp_path)
    except Exception as e:
        error_message = str(e)
        videos_processing_errors_total.inc()
    finally:
        # удаляем временный файл
        try:
            os.remove(temp_path)
        except OSError:
            pass

    processing_time = time.monotonic() - start_time
    videos_processing_time_seconds.observe(processing_time)

    # записываем результат в БД
    db_result = AnalysisResult(
        filename=filename,
        has_motion=has_motion,
        processing_time_seconds=processing_time,
        error_message=error_message,
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    if error_message is None:
        videos_processed_total.inc()

    return db_result


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root():
    return {"status": "ok", "message": "Video analyzer service is running"}
