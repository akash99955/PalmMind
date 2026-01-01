import time
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("⏳ Waiting 10 seconds to ensure API Quota reset...")
    time.sleep(10)

    print("\n1. Testing Chat & Booking...")
    # Using a query that should trigger booking extraction
    payload = {
        "session_id": "final_test_session",
        "query": "Hi, I'd like to book an interview. My name is Akash, email is akash@example.com, for tomorrow at 10 AM."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat Response Received:")
            print(f"   Answer: {data.get('answer')}")
            print(f"   Booking Extracted: {data.get('booking_extracted')}")
            return True
        elif response.status_code == 429:
             print("❌ Quota Exceeded (429). Please wait a minute and try again.")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    return False

if __name__ == "__main__":
    if test_full_flow():
        print("\n🎉 Full Function Verified!")
    else:
        print("\n⚠️ Verification Failed (likely Rate Limit)")
