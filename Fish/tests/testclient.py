from fastapi.testclient import TestClient
from app.main import app
from app.core.auth.jwt import create_access_token

client = TestClient(app)

# create a test token
token = create_access_token({"sub": "cho@example.com", "id": 1})

headers = {"Authorization": f"Bearer {token}"}

response = client.post(
    "/workspaces/2/sources/upload",
    headers=headers,
    files={"file": open("/tmp/tmpzady6_tm.pdf", "rb")}
)
print(response.json())
