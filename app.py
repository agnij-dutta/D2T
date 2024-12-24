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

# def get_subscribed_pods(userid):
#     # Replace with your logic to get the actual list of names
#     return None

# def get_my_pods(userid):
#     return None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# @app.route('/')
# def index():
#     return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        usr = request.form.get("username")
        pwd = request.form.get("password")

        if usr and pwd:
            user = User.query.filter_by(username=usr).first()

            if user and user.check_password(pwd):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password.", "error")
        else:
            flash("Both username and password are required.", "error")

    return render_template('login.html')

@app.route("/", methods=['GET'])
@login_required
def dashboard():
    my_pods = Subjects.query.filter_by(prof_list=str(current_user.user_id)).all()  # Fetch created pods
    subscribed_pods = JoinRequest.query.filter_by(user_id=current_user.user_id).all()  # Fetch subscribed pods

    return render_template('dashboard.html', my_pods=my_pods, subscribed_pods=subscribed_pods)

@app.route("/search", methods=['GET'])
@login_required
def search_subjects():
    query = request.args.get('q', '')
    subjects = Subjects.query.filter(Subjects.sname.contains(query)).all()
    return render_template("search_results.html", subjects=subjects)

@app.route("/request_join/<int:subject_id>", methods=['POST'])
@login_required
def request_join(subject_id):
    role = request.form.get('role')  # 'student' or 'professor'
    subject = Subjects.query.get_or_404(subject_id)
    
    # Create notification for admin
    notification = JoinRequest(
        user_id=current_user.user_id,
        subject_id=subject_id,
        role=role,
        status='pending'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Join request sent!', 'success')
    return redirect(url_for('dashboard'))

@app.route("/createpod", methods=['GET', 'POST'])
@login_required
def createpod():
    if not current_user.is_authenticated:
        flash("You need to log in first!", "danger")
        return redirect(url_for('login'))

    if not current_user.is_admin:
        flash("Only admins can create PODs", "error")
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        sname = request.form.get("pod-name")
        video_url = request.form.get("video_url")  # Get the video URL from the form
        
        if not current_user.is_authenticated:
            flash("You need to log in first!", "danger")
            return redirect(url_for('login'))

        new_subject = Subjects(sname=sname,prof_list=str(current_user.user_id))
        db.session.add(new_subject)
        db.session.commit()

        # # Retrieve the subject_id after committing
        subject_id = new_subject.subject_id
        session['subject_id'] = subject_id
        
        try:
            return redirect(url_for("process_video"))

        except Exception as e:
            flash(f"Error processing video: {str(e)}", "error")
            return redirect(url_for("dashboard"))

        # return redirect(url_for("view_pod", subject_id=subject_id))
        
    return render_template("createpod.html")

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

@app.route('/process', methods=['POST'])
def process_video():
    try:
        url = request.form.get('video_url')  # Get the video URL from the form 
        subject_id = session.get('subject_id')  # Get the subject ID from the session

        # Debugging: Log the received values
        print(f"[DEBUG] Received URL: {url}")
        print(f"[DEBUG] Received Subject ID: {subject_id}")

        if not url or not subject_id:
            return jsonify({'error': 'URL and subject ID are required'}), 400

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
                subject_id=subject_id  # Now subject_id is defined
            )
            db.session.add(new_lecture)
            db.session.commit()

        except Exception as e:
            print(f"[ERROR] Failed to generate AI content: {str(e)}")
            return jsonify({'error': f'Failed to generate AI content: {str(e)}'}), 500

        # Redirect to the pod view after processing
        return redirect(url_for('view_pod', subject_id=subject_id))

    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/notifications")
@login_required
def notifications():
    if not current_user.is_admin:
        flash("Access denied", "error")
        return redirect(url_for('dashboard'))
        
    pending_requests = JoinRequest.query.filter_by(status='pending').all()
    return render_template("notifications.html", requests=pending_requests)

@app.route("/handle_request/<int:request_id>", methods=['POST'])
@login_required
def handle_request(request_id):
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
        
    join_request = JoinRequest.query.get_or_404(request_id)
    action = request.form.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        subject = Subjects.query.get(join_request.subject_id)
        if join_request.role == 'professor':
            prof_list = subject.prof_list.split(',') if subject.prof_list else []
            prof_list.append(str(join_request.user_id))
            subject.prof_list = ','.join(prof_list)
        else:
            stud_list = subject.stud_list.split(',') if subject.stud_list else []
            stud_list.append(str(join_request.user_id))
            subject.stud_list = ','.join(stud_list)
            
        join_request.status = 'approved'
        db.session.commit()
        
    elif action == 'reject':
        join_request.status = 'rejected'
        db.session.commit()
        
    return redirect(url_for('notifications'))

@app.route("/pod/<int:subject_id>")
@login_required
def view_pod(subject_id):
    subject = Subjects.query.get_or_404(subject_id)
    lectures = Lecture.query.filter_by(subject_id=subject_id).all()
    
    # Check if user has access
    user_id_str = str(current_user.user_id)
    is_professor = user_id_str in (subject.prof_list or '').split(',')
    is_student = user_id_str in (subject.stud_list or '').split(',')
    
    if not (is_professor or is_student or current_user.is_admin):
        flash("Access denied", "error")
        return redirect(url_for('dashboard'))
    
    return render_template("view_pod.html", 
                         subject=subject, 
                         lectures=lectures,
                         is_professor=is_professor)

@app.route("/edit_pod/<int:subject_id>", methods=['GET', 'POST'])
@login_required
def edit_pod(subject_id):
    subject = Subjects.query.get_or_404(subject_id)
    
    if not current_user.is_admin and str(current_user.user_id) not in subject.prof_list.split(','):
        flash("Access denied", "error")
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        lec_name = request.form.get("lecture_name")
        video_url = request.form.get("video_url")
        insti_note = request.files.get("lecture_file").read()
        
        new_lecture = Lecture(
            lec_name=lec_name,
            url=video_url,
            insti_note=insti_note,
            subject_id=subject_id
        )
        
        db.session.add(new_lecture)
        db.session.commit()
        
        flash("Lecture added successfully!", "success")
        return redirect(url_for("view_pod", subject_id=subject_id))
    
    return render_template("edit_pod.html", subject=subject)

@app.route('/logout')
@login_required
def logout():
    logout_user()  # Use Flask-Login's logout_user function
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route("/submit_quiz/<int:lecture_id>", methods=['POST'])
@login_required
def submit_quiz(lecture_id):
    lecture = Lecture.query.get_or_404(lecture_id)
    user_answers = request.form.getlist('answers')  # Assuming answers are sent as a list
    correct_answers = []  # Fetch correct answers from the lecture or quiz data

    # Logic to compare user_answers with correct_answers
    score = sum(1 for i in range(len(user_answers)) if user_answers[i] == correct_answers[i])

    # Save the score
    new_score = Scores(
        lec_id=lecture_id,
        stu_id=current_user.user_id,
        score=score,
        timestmp=datetime.utcnow().isoformat()
    )
    db.session.add(new_score)
    db.session.commit()

    flash(f'Your score: {score}/{len(correct_answers)}', 'success')
    return redirect(url_for('view_pod', subject_id=lecture.subject_id))


if __name__ == '__main__':
    app.run(host = "0.0.0.0", debug=True)
