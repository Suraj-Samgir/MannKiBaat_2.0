from flask import Flask, request, render_template, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json
import re

app = Flask(__name__)

# Database Configurations...
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 
CORS(app)
  
app.app_context().push()

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True)
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)
    posts = db.relationship('CommunityPost', backref='author', lazy=True)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # 1-5 scale
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    is_crisis = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    points = db.Column(db.Integer, default=0)

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

class Feedback(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(7), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(35), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    feed = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

# Crisis Detection Keywords
CRISIS_KEYWORDS = [
    'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
    'cutting', 'overdose', 'worthless', 'hopeless', 'can\'t go on'
]

def detect_crisis(message):
    """Detect potential crisis situations in user messages"""
    message_lower = message.lower()
    crisis_score = 0
    
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            crisis_score += 1
    
    return crisis_score >= 2  # Trigger if 2+ crisis keywords found


# All the routes are written below...

# Route for landing page...
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


# Route for contact....
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        print("post")   
        tempname = request.form['Name']
        tempgender = request.form['Gender']
        tempcountry = request.form['Country']
        tempemail = request.form['Email']
        tempphone = request.form['Phone']
        tempfeed = request.form['Feedback']

        ins = Feedback(name=tempname, gender=tempgender, country=tempcountry, email=tempemail, phone=tempphone, feed=tempfeed)

        db.session.add(ins)
        db.session.commit()

    return render_template('contact.html')

# Route for category selection....
@app.route('/info')
def info():
    return render_template('category.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/community')
def community():
    return render_template('community.html')

# API Routes
@app.route('/api/mood', methods=['POST'])
def log_mood():
    data = request.get_json()
    
    # For demo purposes, using session.
    user_id = session.get('user_id', 1)  # Default to user 1 for demo
    
    mood_entry = MoodEntry(
        user_id=user_id,
        mood_score=data['mood_score'],
        notes=data.get('notes', '')
    )
    
    db.session.add(mood_entry)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Mood logged successfully'})

@app.route('/api/mood/history')
def mood_history():
    user_id = session.get('user_id', 1)
    
    # Get last 7 days of mood entries
    week_ago = datetime.utcnow() - timedelta(days=7)
    moods = MoodEntry.query.filter(
        MoodEntry.user_id == user_id,
        MoodEntry.created_at >= week_ago
    ).order_by(MoodEntry.created_at.desc()).all()
    
    mood_data = [{
        'date': mood.created_at.strftime('%Y-%m-%d'),
        'score': mood.mood_score,
        'notes': mood.notes
    } for mood in moods]
    
    return jsonify(mood_data)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message']
    user_id = session.get('user_id', 1)
    
    # Detect crisis
    is_crisis = detect_crisis(message)
    
    # Generate AI response (simplified - integrate with actual AI service)
    if is_crisis:
        response = "I'm concerned about what you're sharing. You're not alone, and there are people who want to help. Would you like me to connect you with crisis resources?"
    else:
        # Simple response logic - integrate with actual AI service
        if 'anxious' in message.lower():
            response = "I understand you're feeling anxious. Let's try some breathing exercises together. Take a deep breath in for 4 counts..."
        elif 'sad' in message.lower():
            response = "It sounds like you're going through a tough time. Your feelings are valid, and it's okay to feel sad sometimes."
        else:
            response = "Thank you for sharing that with me. How are you feeling right now?"
    
    # Save chat message
    chat_message = ChatMessage(
        user_id=user_id,
        message=message,
        response=response,
        is_crisis=is_crisis
    )
    
    db.session.add(chat_message)
    db.session.commit()
    
    return jsonify({
        'response': response,
        'is_crisis': is_crisis,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/achievements')
def get_achievements():
    user_id = session.get('user_id', 1)
    
    # Get user's achievements
    user_achievements = db.session.query(Achievement).join(UserAchievement).filter(
        UserAchievement.user_id == user_id
    ).all()
    
    achievements_data = [{
        'name': achievement.name,
        'description': achievement.description,
        'icon': achievement.icon,
        'points': achievement.points
    } for achievement in user_achievements]
    
    return jsonify(achievements_data)

@app.route('/api/community/posts')
def get_community_posts():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).limit(10).all()
    
    posts_data = [{
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'category': post.category,
        'likes': post.likes,
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M')
    } for post in posts]
    
    return jsonify(posts_data)

@app.route('/api/community/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    user_id = session.get('user_id', 1)
    
    post = CommunityPost(
        author_id=user_id,
        title=data['title'],
        content=data['content'],
        category=data.get('category', 'general')
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Post created successfully'})

@app.route('/api/affirmations')
def get_affirmations():
    # Sample affirmations - in production, store in database
    affirmations = [
        {
            'text': 'You are stronger than you think and braver than you feel.',
            'type': 'text',
            'category': 'strength'
        },
        {
            'text': 'Every small step forward is progress worth celebrating.',
            'type': 'text',
            'category': 'progress'
        },
        {
            'text': 'Your feelings are valid, and it\'s okay to take time to heal.',
            'type': 'text',
            'category': 'validation'
        }
    ]
    
    return jsonify(affirmations)

@app.route('/api/wellness/suggestions')
def get_wellness_suggestions():
    # Sample wellness suggestions
    suggestions = {
        'sleep': {
            'tip': 'Try to maintain a consistent sleep schedule',
            'target': '8 hours',
            'current_streak': 3
        },
        'exercise': {
            'tip': 'Take a 10-minute walk outside',
            'target': '30 minutes daily',
            'current_streak': 1
        },
        'nutrition': {
            'tip': 'Stay hydrated - aim for 8 glasses of water',
            'target': '8 glasses',
            'current_streak': 5
        }
    }
    
    return jsonify(suggestions)


# Initialize database
def initialize_database():
    """Initialize database tables and sample data"""
    db.create_all()
    
    # Create sample achievements if they don't exist
    if Achievement.query.count() == 0:
        achievements = [
            Achievement(name='First Steps', description='Logged your first mood', icon='🌟', points=10),
            Achievement(name='Week Warrior', description='Logged mood for 7 days straight', icon='🏆', points=50),
            Achievement(name='Community Helper', description='Made your first community post', icon='🤝', points=25),
            Achievement(name='Chat Champion', description='Had 10 conversations with the AI', icon='💬', points=30)
        ]
        
        for achievement in achievements:
            db.session.add(achievement)
        
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        initialize_database()
    
    app.run(debug=True)
