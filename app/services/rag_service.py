import json
from sqlalchemy.orm import Session
from app.db.vector_db import qdrant_handler
from app.db.redis_client import redis_handler
from app.services.llm_service import llm_service
from app.db.models import Booking

class RAGService:
    def _construct_prompt(self, history, context, query):
        system_prompt = """You are a helpful assistant for Palm Mind. You have two main functions:
1. Answer questions based on the provided 'Context' below.
2. Assist users with booking interview appointments.

If the user wants to book an appointment, acknowledge it and be helpful. You do NOT need 'Context' for this.
For other questions, use ONLY the provided context. If the answer is not in the context, say you don't know."""
        
        # Format history
        history_str = ""
        for msg in history:
            history_str += f"{msg['role']}: {msg['content']}\n"
        
        # Format context
        context_str = "\n".join([f"- {c}" for c in context])
        
        final_prompt = f"{system_prompt}\n\nContext:\n{context_str}\n\nHistory:\n{history_str}\nUser: {query}\nAssistant:"
        return final_prompt

    async def chat_with_data(self, session_id: str, query: str, db: Session):
        # 1. Retrieve Context
        query_vector = llm_service.get_query_embedding(query)
        search_results = qdrant_handler.search(query_vector, top_k=3)
        context = [hit.payload['text'] for hit in search_results]

        # 2. Get History
        history = redis_handler.get_history(session_id)
        
        # 3. Generate Answer
        prompt = self._construct_prompt(history, context, query)
        answer = llm_service.generate_response(prompt)
        
        # 4. Update History
        redis_handler.add_message(session_id, "user", query)
        redis_handler.add_message(session_id, "assistant", answer)
        
        # 5. Check for Booking Intent & Extract
        booking_info = self._attempt_booking_extraction(query + " " + answer) 
        # Checking combined text might capture confirmation, but extracting from User query is safer 
        # or separate interaction. Let's just check the User's query for booking details.
        
        booking_extracted = None
        if booking_info:
            # Save booking
            new_booking = Booking(
                name=booking_info.get("name"),
                email=booking_info.get("email"),
                date=booking_info.get("date"),
                time=booking_info.get("time")
            )
            db.add(new_booking)
            db.commit()
            booking_extracted = booking_info

        return {
            "answer": answer,
            "context": context,
            "booking_extracted": booking_extracted
        }

    def _attempt_booking_extraction(self, text: str):
        # Specific prompt to extract JSON
        prompt = f"""
        Extract interview booking details from the following text into JSON format with keys: name, email, date, time.
        If any information is missing, DO NOT make it up. Return an empty string "" for missing fields.
        Text: "{text}"
        JSON:
        """
        try:
            response = llm_service.generate_response(prompt)
            # Clean up response
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            print(f"DEBUG: Extracted Raw JSON: {cleaned_response}")
            
            data = json.loads(cleaned_response)
            
            # Check for required fields
            missing = []
            for k in ["name", "email", "date", "time"]:
                if k not in data or not data[k]:
                    missing.append(k)
            
            if not missing:
                print("DEBUG: All fields present. Booking valid.")
                return data
            else:
                print(f"DEBUG: Missing fields: {missing}")
                return None
        except Exception as e:
            print(f"DEBUG: Booking Extraction Failed: {e}")
            return None

rag_service = RAGService()
