import httpx
import time
import subprocess
import os

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "test-token"
HEADERS = {"Authorization": f"Bearer {TEST_TOKEN}"}

def test_health():
    print("Testing /health...")
    response = httpx.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}, Content: {response.json()}")
    assert response.status_code == 200

def test_me():
    print("\nTesting /me (Protected)...")
    response = httpx.get(f"{BASE_URL}/me", headers=HEADERS)
    print(f"Status: {response.status_code}, Content: {response.json()}")
    assert response.status_code == 200
    return response.json()

def test_progress(child_id):
    print(f"\nTesting /progress/{child_id} (GET)...")
    response = httpx.get(f"{BASE_URL}/progress/{child_id}", headers=HEADERS)
    print(f"Status: {response.status_code}, Content: {response.json()}")
    assert response.status_code == 200
    
    print(f"\nTesting /progress/{child_id} (PUT)...")
    update_data = {"coins": 100, "points": 50}
    response = httpx.put(f"{BASE_URL}/progress/{child_id}", headers=HEADERS, json=update_data)
    print(f"Status: {response.status_code}, Content: {response.json()}")
    assert response.status_code == 200
    assert response.json()["profile"]["coins"] == 100

def test_unauthorized():
    print("\nTesting unauthorized access...")
    response = httpx.get(f"{BASE_URL}/me")
    print(f"Status: {response.status_code}, Content: {response.json()}")
    assert response.status_code == 401

def test_content(): 
    print("\nTesting /lessons (Protected)...")
    response = httpx.get(f"{BASE_URL}/lessons", headers=HEADERS)
    print(f"Status: {response.status_code}, Lessons found: {len(response.json())}")
    assert response.status_code == 200

    print("\nTesting /challenges (Protected)...")
    response = httpx.get(f"{BASE_URL}/challenges", headers=HEADERS)
    print(f"Status: {response.status_code}, Challenges found: {len(response.json())}")
    assert response.status_code == 200

if __name__ == "__main__":
    print("Starting API tests...")
    try:
        test_health()
        test_unauthorized()
        me_data = test_me()
        test_content()
        test_progress("test-child")
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTests failed: {e}")
        print("Make sure the server is running with 'uvicorn main:app --reload'")
