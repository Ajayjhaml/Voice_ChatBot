import requests
#just check the file
def test_fastapi_response():
    url = "http://127.0.0.1:8000/generate"
    payload = {"instruction": "What is the capital of France?"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    assert "output" in response.json()
    print("✅ FastAPI responded with:", response.json()["output"])

if __name__ == "__main__":
    test_fastapi_response()
