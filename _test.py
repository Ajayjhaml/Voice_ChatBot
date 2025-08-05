import requests

def test_fastapi_response():
    url = "http://127.0.0.1:8000/generate"
    payload = {
        "instruction": "Translate to Hindi",
        "input": "Hello, how are you?",
        "max_tokens": 50,
        "temperature": 0.5
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 200
    assert "response" in response.json()
    print("✅ FastAPI responded successfully.")

if __name__ == "__main__":
    test_fastapi_response()
