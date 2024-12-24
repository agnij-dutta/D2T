import os
import google.generativeai as genai

class FlashcardService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def create_flashcards(self, text):
        print("[DEBUG] Generating flashcards using Gemini...")
        
        prompt = """Create 30 flashcards from this text. Format each flashcard exactly as:
        Q: (question)
        A: (answer)

        Make questions test key concepts. Keep answers concise.

        Text: {text}"""
        
        try:
            response = self.model.generate_content(prompt.format(text=text[:4000]))
            result = response.text
            print(f"[DEBUG] Raw flashcard response: {result[:200]}...")
            
            flashcards = []
            current_card = {}
            
            lines = [line.strip() for line in result.split('\n') if line.strip()]
            
            for line in lines:
                if line.startswith('Q:'):
                    if current_card and 'question' in current_card and 'answer' in current_card:
                        flashcards.append(current_card.copy())
                    current_card = {"question": line[2:].strip()}
                elif line.startswith('A:') and 'question' in current_card:
                    current_card["answer"] = line[2:].strip()
                    flashcards.append(current_card.copy())
                    current_card = {}
            
            print(f"[DEBUG] Successfully created {len(flashcards)} flashcards")
            return flashcards
            
        except Exception as e:
            print(f"[ERROR] Failed to generate flashcards: {str(e)}")
            return []