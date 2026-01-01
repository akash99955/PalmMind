import requests
import os
import time

BASE_URL = "http://localhost:8000"
SEPARATOR = "-" * 50

def upload_document():
    print(f"\n{SEPARATOR}")
    print("📂 DOCUMENT UPLOAD")
    print(f"{SEPARATOR}")
    path = input("Enter absolute path to PDF or TXT file: ").strip()
    if not os.path.exists(path):
        print("❌ File not found.")
        return

    print("Uploading... (this may take a moment)")
    try:
        files = {'file': open(path, 'rb')}
        response = requests.post(f"{BASE_URL}/ingest", files=files)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Document processed into {data['data']['chunks']} chunks.")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def chat_session():
    print(f"\n{SEPARATOR}")
    print("💬 CHAT BOT (Type 'exit' to quit)")
    print("Features: RAG (Ask about docs) | Booking (Ask to book interview)")
    print(f"{SEPARATOR}")
    
    session_id = f"session_{int(time.time())}"
    
    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ['exit', 'quit']:
            break
        if not query:
            continue
            
        payload = {"session_id": session_id, "query": query}
        
        try:
            print("Bot: (Typing...)")
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Bot: {data['answer']}")
                
                # Check for booking
                if data.get('booking_extracted'):
                    b = data['booking_extracted']
                    print(f"\n📅 [SYSTEM] APPOINTMENT BOOKED!")
                    print(f"   Name:  {b.get('name')}")
                    print(f"   Email: {b.get('email')}")
                    print(f"   Date:  {b.get('date')}")
                    print(f"   Time:  {b.get('time')}")
            
            elif response.status_code == 429:
                print("⚠️  Bot is busy (Rate Limit). Please wait a few seconds and try again.")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")

def main():
    while True:
        print(f"\n{SEPARATOR}")
        print("🤖 RAG BACKEND MANAGER")
        print(f"{SEPARATOR}")
        print("1. Upload a Document")
        print("2. Start Chat")
        print("3. Exit")
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == '1':
            upload_document()
        elif choice == '2':
            chat_session()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    print("Checking server status...")
    try:
        requests.get(BASE_URL)
        main()
    except:
        print("❌ Server is NOT running.")
        print("Please run: uvicorn app.main:app --host 0.0.0.0 --port 8000")
