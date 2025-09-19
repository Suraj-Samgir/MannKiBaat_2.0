from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from datetime import datetime
from categories_data import categories
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Database Configurations...
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

# Table for User registration...
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

    lifestyle = db.relationship('Lifestyle', backref='user', uselist=False)

    def __init__(self, firstName, lastName, email, phone, password, gender, birthDate, eduLevel, fieldOfStudy):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.phone = phone
        # store hashed password as utf-8 string
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.gender = gender
        self.birthDate = birthDate
        self.eduLevel = eduLevel
        self.fieldOfStudy = fieldOfStudy

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# Table for lifestyle data...
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

# Table for category selection and problem definition...
class UserCategorySelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdb.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)          # e.g., "Health"
    subcategory = db.Column(db.String(100), nullable=False)      # e.g., "Poor sleep cycle"
    description = db.Column(db.Text, nullable=True)              # User's detailed problem description
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("Userdb", backref="category_selections")

# Creating all the tables defined above...
with app.app_context():
    db.create_all()

# --- Gemini API Configuration ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")
genai.configure(api_key=API_KEY)

# --- Chat Session Management ---
# In-memory chat sessions (lost on restart)
chat_sessions = {}

def create_initial_prompt(user, lifestyle, categories):
    """Creates a personalized initial prompt for the AI based on user data."""
    prompt = (
        "You are a friendly and empathetic student wellness chatbot named 'Dost'. "
        "Your purpose is to provide support and practical advice in a mix of English and Hindi (Hinglish). "
        "Keep your responses concise, supportive, and easy to understand.\n\n"
        "Here is the context for the student you are talking to:\n"
        f"- Their name is {user.firstName}.\n"
        f"- They study {user.fieldOfStudy}.\n"
        f"- Their lifestyle info: Sleeps {lifestyle.sleepHrs} hours/night, Stress Level is {lifestyle.stressLevel}/10.\n"
        "- The main challenges they've identified are:\n"
    )
    for selection in categories:
        prompt += (
            f"  - Under '{selection.category}', the specific issue is '{selection.subcategory}' "
            f"and the description is '{selection.description}'.\n"
        )

    prompt += "\nBegin the conversation by warmly greeting them by their first name and gently acknowledging one of their key challenges (e.g., stress or a specific category they chose). Ask them how you can help today."
    return prompt

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

        session['user_id'] = new_user.id

        return redirect(url_for('lifestyle'))

    return render_template('register.html', show_quickLinks=True)

# Route for lifestyle data...
@app.route('/lifestyle', methods=['GET', 'POST'])
def lifestyle():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('register'))  # fallback if session lost

        new_lifestyle = Lifestyle(
            user_id=user_id,
            diet=request.form['diet'],
            physicalActivity=request.form['physicalActivity'],
            socialInteraction=request.form['socialInteraction'],
            relaxHabit=request.form['relaxHabit'],
            screenTime=int(request.form['screenTime']),
            stressLevel=int(request.form['stressLevel']),
            sleepHrs=int(request.form['sleepHrs'])
        )

        db.session.add(new_lifestyle)
        db.session.commit()

        return redirect(url_for('category'))

    return render_template('lifestyle.html', show_quickLinks=False)

# Route for category selection....
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

        session.pop('user_id', None)

        return redirect(url_for('login'))

    return render_template('category.html', show_quickLinks=False, categories=categories)

# Route after login successful, showing AI Dashboard...
@app.route('/dashboard')
def dashboard():
    email = session.get('email')  # safer than session['email']
    if email:
        user = Userdb.query.filter_by(email=email).first()
        if not user:
            return redirect('/login')  # fallback if no user found

        lifestyle = Lifestyle.query.filter_by(user_id=user.id).first()
        categories_sel = UserCategorySelection.query.filter_by(user_id=user.id).all()

        return render_template(
            "dashboard.html",
            user=user,
            lifestyle=lifestyle,
            categories=categories_sel
        )
    else:
        return redirect('/login')

# Route for logout ....
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
