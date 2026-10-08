from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.measure import router as measure_router

app = FastAPI(
    title="Geospatial File Measurement API",
    version="1.0.0",
    description="Upload geospatial data and receive geometry measurements.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(measure_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
