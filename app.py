from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from datetime import datetime
from categories_data import categories

app = Flask(__name__)

#Database Configurations...
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)   
app.app_context().push()

# Table for User registeration...
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

# All the routes are written below...

# Route for landing page...
@app.route('/')
def index():
    return render_template('index.html', show_quickLinks=True)

# Route for Login Page...
@app.route('/login', methods = ['GET','POST'])
def login():
    return render_template('login.html', show_quickLinks=True)


# Route for registeration....
@app.route('/register', methods = ['GET','POST'])
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

        new_user = Userdb(firstName, lastName, email, phone, password, gender, birthDate, eduLevel, fieldOfStudy)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id

        return redirect(url_for('lifestyle'))

    return render_template('register.html', show_quickLinks=True)

#Route for lifestyle data...
@app.route('/lifestyle', methods = ['GET','POST'])
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
@app.route('/category', methods = ['GET','POST'])
def category():

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('register'))

    if request.method == 'POST':
        category = request.form.get('category')
        subcategory = request.form.get('subcategory')
        description = request.form.get('description')

        new_selection = UserCategorySelection(
            user_id=user_id,
            category=category,
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
    pass

if __name__ == "__main__":
    app.run(debug=True)