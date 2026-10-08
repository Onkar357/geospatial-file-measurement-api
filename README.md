# Geospatial File Measurement API

FastAPI service for uploading GeoJSON, KML/KMZ, and zipped Shapefile datasets and returning geometry measurements.

## Features
- GeoJSON, KML/KMZ and ZIP Shapefile uploads
- Polygon/MultiPolygon area measurement
- LineString/MultiLineString length measurement
- Point/MultiPoint support
- CRS-aware transformation to a metric CRS (UTM when possible)
- Feature properties and geometry type in responses
- SQLite processing metadata
- File-size and validation limits
- ZIP path-traversal protection
- Docker support
- Automated tests

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs

## API
`POST /api/v1/measure` with multipart field `file`.

Response contains processing metadata and measurements for every feature.

## Example
The included sample KML uses EPSG:4326. Measurements are calculated after transformation to a suitable projected CRS.

## Docker
```bash
docker build -t geospatial-measurement-api .
docker run --rm -p 8000:8000 geospatial-measurement-api
```
