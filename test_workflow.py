import requests
import sys

BASE_URL = "http://localhost:8000"

def test_ingest():
    print("Testing Ingestion...")
    # Create dummy file
    with open("test_doc.txt", "w") as f:
        f.write("Google DeepMind is an artificial intelligence research laboratory which is a subsidiary of Alphabet Inc. It was founded in September 2010. DeepMind was acquired by Google in 2014.")
    
    files = {'file': open('test_doc.txt', 'rb')}
    data = {'strategy': 'recursive'}
    response = requests.post(f"{BASE_URL}/ingest", files=files, data=data)
    print("Ingest Response:", response.json())
    return response.status_code == 200

def test_chat():
    print("\nTesting Chat...")
    payload = {
        "session_id": "test_session_1",
        "query": "When was DeepMind acquired by Google?"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print("Chat Response:", response.json())
    return response.status_code == 200

def test_booking():
    print("\nTesting Booking...")
    payload = {
        "session_id": "test_session_1",
        "query": "Book an interview for Alice at alice@example.com on 2025-05-20 at 2pm"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print("Booking Response:", response.json())
    return response.status_code == 200

import time

if __name__ == "__main__":
    try:
        ingest_ok = test_ingest()
        time.sleep(10)
        chat_ok = test_chat()
        time.sleep(10)
        booking_ok = test_booking()
        
        if ingest_ok and chat_ok and booking_ok:
            print("\nAll Tests Passed!")
        else:
            print("\nSome Tests Failed.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Ensure the server is running on localhost:8000")
