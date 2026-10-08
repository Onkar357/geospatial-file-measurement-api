from pathlib import Path

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
MAX_UNZIPPED_SIZE = 200 * 1024 * 1024
ALLOWED_EXTENSIONS = {".geojson", ".json", ".kml", ".kmz", ".zip"}
DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "metadata.db"
DATA_DIR.mkdir(exist_ok=True)
