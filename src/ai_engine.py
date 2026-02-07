import ollama
from .config import Config
import logging

class AIEngine:
    def __init__(self):
        self.model = Config.OLLAMA_MODEL

    def generate_reply(self, sender, subject, body, history=[], context=""):
        """
        Generate a reply using the local LLM with context and history.
        """
        
        history_text = "\n".join([f"From: {msg.from_}\nDate: {msg.date}\nSubject: {msg.subject}\nBody: {msg.text[:500]}...\n---" for msg in history]) if history else "No previous history."

        prompt = f"""You are a helpful email assistant. Please draft a professional and courteous reply to the following email.
        
        --- CONTEXT & RESOURCES ---
        The user has provided the following background information to help you answer accurately:
        {context}
        ---------------------------

        --- PAST CONversation HISTORY (Chronological) ---
        {history_text}
        -----------------------------------------------
        
        --- NEW INCOMING EMAIL ---
        SENDER: {sender}
        SUBJECT: {subject}
        
        EMAIL BODY:
        {body}
        
        INSTRUCTIONS:
        - **IMPORTANT**: Provide the reply ONLY to the specific "NEW INCOMING EMAIL" below. Do NOT reply to the "PAST CONVERSATION HISTORY".
        - The conversation history is provided ONLY for context so you understand what was said before.
        - Use the CONTEXT to provide accurate specific details if relevant.
        - Keep the tone professional but friendly.
        - Address the sender by name if possible.
        - Do not include placeholders like [Your Name], sign off simply with "Best regards," followed by nothing else (the user will sign it).
        - If the email is spam or irrelevant, reply with "IGNORE".
        """

        try:
            response = ollama.chat(model=self.model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            return response['message']['content']
        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            return None

if __name__ == "__main__":
    # Test
    ai = AIEngine()
    print(ai.generate_reply("test@example.com", "Hello", "Just wanted to say hi!"))
