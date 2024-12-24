import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from services.video_service import VideoService
from services.ai_service import AIService
from services.flashcard_service import FlashcardService
from services.quiz_service import QuizService
from flask_cors import CORS
from model import db, User, Subjects, Lecture, Student_notes, Scores, JoinRequest
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tentultalaunitediitians'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirect to login page if not authenticated

# Initialize the database
db.init_app(app)

# Create the database tables within an application context
with app.app_context():
    db.create_all()

CORS(app)

video_service = VideoService()
ai_service = AIService()
flashcard_service = FlashcardService()
quiz_service = QuizService()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():

    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    print(f"\n[DEBUG] Processing video URL: {url}")

    # Get transcript
    print("[DEBUG] Fetching transcript...")
    try:
        transcript = video_service.get_transcript(url)
        print(f"[DEBUG] Transcript length: {len(transcript)} characters")
    except Exception as e:
        print(f"[ERROR] Failed to get transcript: {str(e)}")
        return jsonify({'error': f'Failed to get transcript: {str(e)}'}), 500

    # Generate AI content
    try:
        print("\n[DEBUG] Generating summary...")
        summary = ai_service.generate_summary(transcript)
        print(f"[DEBUG] Summary generated: {summary[:100]}...")

        print("\n[DEBUG] Generating chapters...")
        chapters = ai_service.generate_chapters(transcript)
        print(f"[DEBUG] Generated {len(chapters)} chapters")
        
        print("\n[DEBUG] Generating notes...")
        notes = ai_service.generate_notes(transcript)
        print(f"[DEBUG] Generated notes")
        
        print("\n[DEBUG] Generating flashcards...")
        flashcards = flashcard_service.create_flashcards(transcript)
        print(f"[DEBUG] Generated {len(flashcards)} flashcards")

        print("\n[DEBUG] Generating quiz...")
        quiz = quiz_service.create_quiz(transcript)
        print(f"[DEBUG] Generated quiz with {len(quiz)} questions")

                # Save the lecture and AI outputs to the database
        new_lecture = Lecture(
            lec_name="Generated Lecture",  # You can customize this
            url=url,
            insti_note=request.files.get("lecture_file").read(),  # Save uploaded file if needed
            trans=transcript,
            summary=summary,
            flashcard=flashcards,
            quiz=quiz
        )
        db.session.add(new_lecture)
        db.session.commit()


    except Exception as e:
        print(f"[ERROR] Failed to generate AI content: {str(e)}")
        return jsonify({'error': f'Failed to generate AI content: {str(e)}'}), 500
    return jsonify({
        'transcript': transcript,
        'summary': summary,
        'chapters': chapters,
        'notes': notes,
        'flashcards': flashcards
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        usr = request.form.get("username")
        pwd = request.form.get("password")

        if usr and pwd:
            user = User.query.filter_by(username=usr).first()

            if user and check_password_hash(user.password, pwd):  # Use check_password_hash for security
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password.", "error")
        else:
            flash("Both username and password are required.", "error")

    return render_template('login.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        is_admin = request.form.get("is_admin") == "1"

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            is_admin=is_admin
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Use Flask-Login's logout_user function
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host = "0.0.0.0", debug=True)