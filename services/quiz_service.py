import os
import google.generativeai as genai

class QuizService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def create_quiz(self, text):
        print("[DEBUG] Generating quiz using Gemini...")
        
        prompt = """Create a quiz with 10 multiple choice questions from this text. 
        For each question, provide 4 options (or 2 options for True/False).
        Format exactly as:
        Q1: (question)
        a) option1
        b) option2
        c) option3
        d) option4
        CORRECT: (correct_option_letter)

        Make questions test understanding. Ensure no repeated questions or redundant options.
        
        Text: {text}"""
        
        try:
            response = self.model.generate_content(prompt.format(text=text[:4000]))
            result = response.text
            print(f"[DEBUG] Raw quiz response: {result[:200]}...")
            
            questions = []
            current_question = None
            current_options = []
            
            for line in result.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Q'):
                    if current_question and current_options:
                        questions.append({
                            'question': current_question,
                            'options': current_options,
                            'correct': ''  # Will be filled later
                        })
                    current_question = line[line.find(':')+1:].strip()
                    current_options = []
                elif line.startswith(('a)', 'b)', 'c)', 'd)')):
                    current_options.append(line[2:].strip())
                elif line.startswith('CORRECT:'):
                    if current_question and current_options:
                        questions.append({
                            'question': current_question,
                            'options': current_options,
                            'correct': line[8:].strip()
                        })
                        current_question = None
                        current_options = []
            
            # Add the last question if exists
            if current_question and current_options:
                questions.append({
                    'question': current_question,
                    'options': current_options,
                    'correct': ''
                })
            
            print(f"[DEBUG] Successfully created {len(questions)} questions")
            return questions
            
        except Exception as e:
            print(f"[ERROR] Failed to generate quiz: {str(e)}")
            return [] 