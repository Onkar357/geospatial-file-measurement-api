from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rejects_unsupported_file():
    response = client.post(
        "/api/v1/measure",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_rejects_unsafe_zip():
    payload = BytesIO()
    with ZipFile(payload, "w") as z:
        z.writestr("../../evil.txt", "bad")
    response = client.post(
        "/api/v1/measure",
        files={"file": ("data.zip", payload.getvalue(), "application/zip")},
    )
    assert response.status_code == 400
