import json
from sqlalchemy.orm import Session
from app.db.redis_client import redis_handler
from app.services.llm_service import llm_service
from app.db.models import Booking, DocumentMetadata

class RAGService:
    def _construct_prompt(self, history, context_text, query):
        system_prompt = """You are a helpful assistant for Palm Mind. You have two main functions:
1. Answer questions based on the provided 'Context' below.
2. Assist users with booking interview appointments.

If the user wants to book an appointment, acknowledge it and be helpful. You do NOT need 'Context' for this.
For other questions, use ONLY the provided context. If the answer is not in the context, say you don't know."""
        
        # Format history
        history_str = ""
        for msg in history:
            history_str += f"{msg['role']}: {msg['content']}\n"
        
        final_prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nHistory:\n{history_str}\nUser: {query}\nAssistant:"
        return final_prompt

    async def chat_with_data(self, session_id: str, query: str, db: Session):
        # 1. Retrieve all stored document content as context
        docs = db.query(DocumentMetadata).all()
        context_text = "\n\n".join([f"Source: {doc.filename}\n{doc.content}" for doc in docs])

        # 2. Get History
        history = redis_handler.get_history(session_id)
        
        # 3. Generate Answer
        prompt = self._construct_prompt(history, context_text, query)
        answer = llm_service.generate_response(prompt)
        
        # 4. Update History
        redis_handler.add_message(session_id, "user", query)
        redis_handler.add_message(session_id, "assistant", answer)
        
        # 5. Check for Booking Intent & Extract
        booking_info = self._attempt_booking_extraction(query + " " + answer) 
        
        booking_extracted = None
        if booking_info:
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
            "context_summary": f"Using {len(docs)} documents as context",
            "booking_extracted": booking_extracted
        }

    def _attempt_booking_extraction(self, text: str):
        prompt = f"""
        Extract interview booking details from the following text into JSON format with keys: name, email, date, time.
        If any information is missing, DO NOT make it up. Return an empty string "" for missing fields.
        Text: "{text}"
        JSON:
        """
        try:
            response = llm_service.generate_response(prompt)
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_response)
            
            missing = []
            for k in ["name", "email", "date", "time"]:
                if k not in data or not data[k]:
                    missing.append(k)
            
            if not missing:
                return data
            else:
                return None
        except Exception:
            return None

rag_service = RAGService()
