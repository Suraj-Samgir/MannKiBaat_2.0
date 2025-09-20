# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import json
import os
from datetime import datetime, date, timedelta
from categories_data import categories
import google.generativeai as genai
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()



# Table for User registration...
app = Flask(__name__)
# Use a persistent secret in production; for dev this is fine
app.secret_key = os.urandom(24)

# Database Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# MODELS
# ---------------------------

class Userdb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # hashed password
    gender = db.Column(db.String(7), nullable=False)
    birthDate = db.Column(db.Date, nullable=False)
    eduLevel = db.Column(db.String(30), nullable=False)
    fieldOfStudy = db.Column(db.String(30), nullable=False)

    # Activity streak fields
    activity_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)

    # initializer and password check
    def __init__(self, firstName, lastName, email, phone, password, gender, birthDate, eduLevel, fieldOfStudy):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.phone = phone
        # store hashed password as utf-8 string
        # store hashed password
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.gender = gender
        self.birthDate = birthDate
        self.eduLevel = eduLevel
        self.fieldOfStudy = fieldOfStudy

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Table for lifestyle data...

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    est_time = db.Column(db.String(50), nullable=True)   # e.g. "2-5 min"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserActivityCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdb.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('Userdb', backref='completions')
    activity = db.relationship('Activity')


# If the rest of your app expects 'Lifestyle', reintroduce it (original file had it commented).
class Lifestyle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdb.id'), nullable=False, unique=True)
    diet = db.Column(db.String(50), nullable=False)
    physicalActivity = db.Column(db.String(50), nullable=False)
    socialInteraction = db.Column(db.String(50), nullable=False)
    relaxHabit = db.Column(db.String(50), nullable=False)
    screenTime = db.Column(db.Integer, nullable=False)
    stressLevel = db.Column(db.Integer, nullable=False)
    sleepHrs = db.Column(db.Integer, nullable=False)

    user = db.relationship("Userdb", backref="lifestyle")


class UserCategorySelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdb.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("Userdb", backref="category_selections")


# ---------------------------
# CREATE TABLES & SEED ACTIVITIES
# ---------------------------
with app.app_context():
    # ensure instance folder exists
    instance_dir = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_dir, exist_ok=True)

    # create DB tables
    db.create_all()

# --- Gemini API Configuration ---
    # seed activities from static/data/activities.json if empty
    try:
        if Activity.query.count() == 0:
            data_path = os.path.join(app.root_path, 'static', 'data', 'activities.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    items = json.load(f)
                for it in items:
                    a = Activity(title=it.get('title', '')[:200],
                                 description=it.get('description', ''),
                                 est_time=it.get('est_time', ''))
                    db.session.add(a)
                db.session.commit()
                print(f"Seeded {len(items)} activities into the database.")
    except Exception as e:
        # if the DB file existed but table not created, this will surface — helpful while debugging
        print("Seeding error (non-fatal):", e)


# ---------------------------
# Gemini / Google AI configuration
# ---------------------------
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    # keep failing early so developer knows to set the key (but if you want to run without chat, you can comment this out)
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")
genai.configure(api_key=API_KEY)

# --- Chat Session Management ---
# In-memory chat sessions (lost on restart)

# ---------------------------
# Chat session storage (in-memory)
# ---------------------------
chat_sessions = {}


def create_initial_prompt(user, lifestyle, categories_list):
    """Creates a personalized initial prompt for the AI based on user data."""
    prompt = (
        "You are a friendly and empathetic student wellness chatbot named 'Dost'. "
        "Your purpose is to provide support and practical advice in a mix of English and Hindi (Hinglish). "
        "Keep your responses concise, supportive, and easy to understand.\n\n"
        "Here is the context for the student you are talking to:\n"
        f"- Their name is {user.firstName}.\n"
        f"- They study {user.fieldOfStudy}.\n"
        f"- Their lifestyle info: Sleeps {getattr(lifestyle, 'sleepHrs', 'N/A')} hours/night, Stress Level is {getattr(lifestyle, 'stressLevel', 'N/A')}/10.\n"
        "- The main challenges they've identified are:\n"
    )
    for selection in categories:
        prompt += (
            f"  - Under '{selection.category}', the specific issue is '{selection.subcategory}' "
            f"and the description is '{selection.description}'.\n"
        )
    for selection in categories_list:
        prompt += f"  - Under '{selection.category}', the specific issue is '{selection.subcategory}'.\n"

    prompt += "\nBegin the conversation by warmly greeting them by their first name and gently acknowledging one of their key challenges (e.g., stress or a specific category they chose). Ask them how you can help today."
    return prompt


# ---------------------------
# ROUTES
# ---------------------------

    try:
        # Retrieve or create a chat session for the current user
        if email not in chat_sessions:
            # Fetch user data to create a personalized context for the first time
            user = Userdb.query.filter_by(email=email).first()
            lifestyle = Lifestyle.query.filter_by(user_id=user.id).first()
            categories_sel = UserCategorySelection.query.filter_by(user_id=user.id).all()

            if not all([user, lifestyle]):
                return jsonify({"error": "Could not retrieve user data to personalize chat."}), 500

            initial_prompt = create_initial_prompt(user, lifestyle, categories_sel)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Start a new chat session with this context
            new_chat_session = model.start_chat(history=[
                {"role": "user", "parts": [initial_prompt]},
                {"role": "model", "parts": [f"Hi {user.firstName}! I'm Dost, your personal wellness friend. I can see you're dealing with a few things, and that's completely okay. We can talk about it. What's on your mind right now?"]}
            ])
            chat_sessions[email] = new_chat_session

        # Get the ongoing chat session for the user and send their message
        user_chat = chat_sessions[email]
        response = user_chat.send_message(user_message)

        # Return the model's reply text (adapt as needed depending on genai SDK response shape)
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"An error occurred in /chat route: {e}")
        return jsonify({"error": "Sorry, I'm having a little trouble thinking right now. Please try again in a moment."}), 500

# Route for affirmations ...
@app.route('/affirmation')
def affirmation():
    email = session.get('email')
    if not email:
        return jsonify({"error": "Authentication required. Please log in again."}), 401

    try:
        # Fetch user details
        user = Userdb.query.filter_by(email=email).first()
        lifestyle = Lifestyle.query.filter_by(user_id=user.id).first()
        categories_sel = UserCategorySelection.query.filter_by(user_id=user.id).all()

        if not all([user, lifestyle]):
            return jsonify({"error": "Could not retrieve user data to personalize affirmation."}), 500

        # Build a personalized prompt
        prompt = (
            f"You are an empathetic wellness assistant. "
            f"Generate ONE short, positive, uplifting affirmation. "
            f"Make it motivational, relevant to their challenges and lifestyle. "
            f"They sleep {lifestyle.sleepHrs} hours/night and have a stress level of {lifestyle.stressLevel}/10. "
            "- The main challenges they've identified are:\n"
        )
        for selection in categories_sel:
            prompt += (
                f"  - Under '{selection.category}', the specific issue is '{selection.subcategory}' "
                f"and the description is '{selection.description}'.\n"
            )

        prompt += (
            "\nKeep it under 20 words. "
            "Avoid quotes, numbering, or extra explanations. "
            "Return just the affirmation text. "
            "Make it unique."
        )

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)

        return jsonify({"affirmation": response.text.strip()})

    except Exception as e:
        print(f"Error generating affirmation: {e}")
        return jsonify({"error": "Failed to generate affirmation."}), 500

# Route for landing page...
@app.route('/')
def index():
    return render_template('index.html', show_quickLinks=True)

# Route for Login Page...

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Userdb.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template("login.html", errorMsg="* Invalid Username or Password *")

    return render_template('login.html', show_quickLinks=True)

# Route for registration....

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        gender = request.form['gender']
        birthDate = datetime.strptime(request.form['birthDate'], '%Y-%m-%d').date()
        eduLevel = request.form['eduLevel']
        fieldOfStudy = request.form['fieldOfStudy']

        existing_user = Userdb.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered! Please login."

        # Use the model's constructor (it hashes the password)
        new_user = Userdb(firstName, lastName, email, phone, password, gender, birthDate, eduLevel, fieldOfStudy)
        db.session.add(new_user)
        db.session.commit()

        # store user_id in session so they can fill lifestyle & categories
        session['user_id'] = new_user.id

        return redirect(url_for('lifestyle'))

    return render_template('register.html', show_quickLinks=True)

# Route for lifestyle data...

# app.py
@app.route("/lifestyle", methods=["GET", "POST"])
def lifestyle():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        diet = request.form.get("diet")
        physicalActivity = request.form.get("physicalActivity")
        socialInteraction = request.form.get("socialInteraction")
        relaxHabit = request.form.get("relaxHabit")
        screenTime = int(request.form.get("screenTime"))
        stressLevel = int(request.form.get("stressLevel"))
        sleepHrs = int(request.form.get("sleepHrs"))

        # check if lifestyle record exists
        lifestyle = Lifestyle.query.filter_by(user_id=user_id).first()
        if lifestyle:
            lifestyle.diet = diet
            lifestyle.physicalActivity = physicalActivity
            lifestyle.socialInteraction = socialInteraction
            lifestyle.relaxHabit = relaxHabit
            lifestyle.screenTime = screenTime
            lifestyle.stressLevel = stressLevel
            lifestyle.sleepHrs = sleepHrs
        else:
            lifestyle = Lifestyle(
                user_id=user_id,
                diet=diet,
                physicalActivity=physicalActivity,
                socialInteraction=socialInteraction,
                relaxHabit=relaxHabit,
                screenTime=screenTime,
                stressLevel=stressLevel,
                sleepHrs=sleepHrs
            )
            db.session.add(lifestyle)

        db.session.commit()
        return redirect(url_for("dashboard"))

    # If GET, render lifestyle.html form
    return render_template("lifestyle.html")


# Route for category selection....
@app.route('/activities/random')
def activities_random():
    import json, random

    count = int(request.args.get('count', 5))
    activities = Activity.query.all()

    if not activities:  # fallback to static JSON
        with open('static/data/activities.json') as f:
            activities = json.load(f)
        random.shuffle(activities)
        return jsonify(activities[:count])

    # if DB has rows
    chosen = []
    try:
        chosen = random.sample(activities, min(count, len(activities)))
    except Exception:
        chosen = activities[:count]

    return jsonify([
        {
            'id': a.id,
            'title': a.title,
            'description': a.description or '',
            'est_time': a.est_time or ''
        } for a in chosen
    ])


@app.route('/activities/complete', methods=['POST'])
def activities_complete():
    if 'email' not in session:
        return jsonify({'error': 'login required'}), 401
    user = Userdb.query.filter_by(email=session['email']).first()
    if not user:
        return jsonify({'error': 'user not found'}), 404

    payload = request.json or {}
    activity_id = payload.get('activity_id') or payload.get('id')  # accept both keys
    if not activity_id:
        return jsonify({'error': 'missing activity_id'}), 400

    # Prevent double counting for the same activity on the same day
    today = datetime.utcnow().date()
    already = UserActivityCompletion.query.filter(
        UserActivityCompletion.user_id == user.id,
        UserActivityCompletion.activity_id == activity_id,
        db.func.date(UserActivityCompletion.completed_at) == today
    ).first()
    if already:
        return jsonify({'success': True, 'message': 'already completed today', 'new_streak': user.activity_streak})

    # create completion entry
    completion = UserActivityCompletion(user_id=user.id, activity_id=activity_id)
    db.session.add(completion)

    # update streak: increment if yesterday, reset if older
    if user.last_activity_date == today:
        # already completed something today (but not this activity) => keep streak
        pass
    elif user.last_activity_date == (today - timedelta(days=1)):
        user.activity_streak = (user.activity_streak or 0) + 1
    else:
        user.activity_streak = 1

    user.last_activity_date = today
    db.session.commit()
    return jsonify({'success': True, 'new_streak': user.activity_streak})


@app.route("/activities/streak")
def get_streak():
    if "user_id" not in session:
        return jsonify({"streak": 0})

    user = Userdb.query.get(session["user_id"])
    return jsonify({"streak": user.activity_streak or 0})


@app.route('/category', methods=['GET', 'POST'])
def category():
    if request.method == 'GET':
        return render_template('category.html', show_quickLinks=False, categories=categories)

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))

    if request.method == 'POST':
        category_val = request.form.get('category')
        subcategory = request.form.get('subcategory')
        description = request.form.get('description')

        new_selection = UserCategorySelection(
            user_id=user_id,
            category=category_val,
            subcategory=subcategory,
            description=description
        )
        db.session.add(new_selection)
        db.session.commit()
    category = request.form.get('category')
    subcategory = request.form.get('subcategory')
    description = request.form.get('description')


    # pop temporary session key after finishing onboarding
    session.pop('user_id', None)

    return redirect(url_for('login'))



    return render_template('category.html', show_quickLinks=False, categories=categories)

@app.route('/dashboard')
def dashboard():
    email = session.get('email')  # safer than session['email']
    if email:
        user = Userdb.query.filter_by(email=email).first()
        if not user:
            return redirect('/login')  # fallback if no user found

        lifestyle = Lifestyle.query.filter_by(user_id=user.id).first()
        categories_sel = UserCategorySelection.query.filter_by(user_id=user.id).all()
        categories_list = UserCategorySelection.query.filter_by(user_id=user.id).all()

        return render_template(
            "dashboard.html",
            user=user,
            lifestyle=lifestyle,
            categories=categories_sel,
        )
    else:
        return redirect('/login')

# Route for logout ....

@app.route('/chat', methods=['POST'])
def chat():
    """Handles the chatbot API calls for logged-in users."""
    email = session.get('email')
    if not email:
        return jsonify({"error": "Authentication required. Please log in again."}), 401

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        # Retrieve or create a chat session for the current user
        if email not in chat_sessions:
            # Fetch user data to create a personalized context for the first time
            user = Userdb.query.filter_by(email=email).first()
            lifestyle = Lifestyle.query.filter_by(user_id=user.id).first()
            categories_list = UserCategorySelection.query.filter_by(user_id=user.id).all()

            if not all([user, lifestyle]):
                return jsonify({"error": "Could not retrieve user data to personalize chat."}), 500

            initial_prompt = create_initial_prompt(user, lifestyle, categories_list)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # start a new chat session
            new_chat_session = model.start_chat(history=[
                {"role": "user", "parts": [initial_prompt]},
                {"role": "model", "parts": [f"Hi {user.firstName}! I'm Dost, your personal wellness friend. I can see you're dealing with a few things, and that's completely okay. We can talk about it. What's on your mind right now?"]}
            ])
            chat_sessions[email] = new_chat_session

        # Use ongoing session
        user_chat = chat_sessions[email]
        response = user_chat.send_message(user_message)

        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"An error occurred in /chat route: {e}")
        return jsonify({"error": "Sorry, I'm having a little trouble thinking right now. Please try again in a moment."}), 500


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
 