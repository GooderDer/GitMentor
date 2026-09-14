"""Phase 7：验证 FastAPI 接口和请求校验。"""
from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("def main():\n    pass\n", encoding="utf-8")

    response = client.post("/analyze", json={"repo_path": str(tmp_path)})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == tmp_path.name
    assert body["main_language"] == "Python"
    assert body["readme"] == "README.md"


def test_ask_validates_required_question():
    response = client.post("/ask", json={"repo_path": "."})

    assert response.status_code == 422
    assert response.json()["detail"]
