from fastapi.testclient import TestClient

from travel_concierge.app import app


client = TestClient(app)


def test_health_endpoint():
  response = client.get("/health")

  assert response.status_code == 200
  assert response.json() == {"status": "ok"}


def test_chat_rejects_empty_message():
  response = client.post("/chat", json={"message": ""})

  assert response.status_code == 422