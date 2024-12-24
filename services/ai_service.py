import os
import google.generativeai as genai

class AIService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_summary(self, text):
        prompt = """Summarize this text concisely, focusing on the main points:

        Text: {text}"""
        
        try:
            response = self.model.generate_content(prompt.format(text=text[:4000]))
            return response.text
        except Exception as e:
            print(f"[ERROR] Failed to generate summary: {str(e)}")
            return "Error generating summary. Please try again."

    def generate_chapters(self, text):
        prompt = """Divide this text into chapters with titles and content. Format as:

        Chapter 1: [Title]
        [Content]

        Chapter 2: [Title]
        [Content]

        Text: {text}"""
        
        try:
            response = self.model.generate_content(prompt.format(text=text[:4000]))
            result = response.text
            
            chapters = []
            current_chapter = {"title": "", "content": ""}
            
            for line in result.split('\n'):
                if line.strip().startswith('Chapter'):
                    if current_chapter["title"]:
                        chapters.append(current_chapter)
                    current_chapter = {"title": line.strip(), "content": ""}
                elif line.strip():
                    current_chapter["content"] += line + "\n"
            
            if current_chapter["title"]:
                chapters.append(current_chapter)
            
            return chapters if chapters else [{"title": "Chapter 1", "content": result}]
            
        except Exception as e:
            print(f"[ERROR] Failed to generate chapters: {str(e)}")
            return [{"title": "Chapter 1", "content": "Error generating chapters. Please try again."}]

    def generate_notes(self, text):
        prompt = """Create concise study notes from this text. Format as bullet points with key concepts and important details.

        Text: {text}"""
        
        try:
            response = self.model.generate_content(prompt.format(text=text[:4000]))
            return [note.strip() for note in response.text.split('\n') if note.strip()]
        except Exception as e:
            print(f"[ERROR] Failed to generate notes: {str(e)}")
            return ["Error generating notes. Please try again."]