import requests
import sqlite3
import time

BASE_URL = "http://localhost:8000"
DB_PATH = "sql_app.db"

def make_booking():
    print("🤖 AI: Attempting to book an appointment...")
    
    # payload with all 4 required fields
    query = "Book a meeting for Alice Wonderland at alice@example.com on next Monday at 2pm."
    session_id = f"demo_{int(time.time())}"
    
    payload = {
        "session_id": session_id,
        "query": query
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Server Response:")
            print(f"   Answer: {data['answer']}")
            if data['booking_extracted']:
                print("   🎉 BOOKING EXTRACTED:", data['booking_extracted'])
            else:
                print("   ⚠️  No booking extracted (Check server logs for DEBUG info)")
        elif response.status_code == 429:
            print("❌ Quota Exceeded (429). Google API is busy.")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def check_db():
    print("\n📦 Checking Database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"   found latest row: {row}")
        else:
            print("   (Database is empty)")
    except Exception as e:
        print(f"   DB Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    make_booking()
    check_db()
