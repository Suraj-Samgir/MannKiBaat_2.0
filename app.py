from flask import Flask,request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

#Database Configurations...
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)   
app.app_context().push()

#Creating Table and its columns in database...
class Feedback(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(7),nullable=False)
    country = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(35),nullable=False)
    phone = db.Column(db.Integer,nullable=False)
    feed = db.Column(db.String(250),nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# All the routes are written below...

# Route for landing page...
@app.route('/', methods = ['POST','GET'])
def index():
    return render_template('index.html')


# Route for contact....
@app.route('/contact', methods = ['GET','POST'])
def contact():
    if request.method == 'POST':
        print("post")   
        tempname = request.form['Name']
        tempgender = request.form['Gender']
        tempcountry = request.form['Country']
        tempemail = request.form['Email']
        tempphone = request.form['Phone']
        tempfeed = request.form['Feedback']

        ins = Feedback(name=tempname, gender=tempgender, country=tempcountry, email=tempemail, phone=tempphone,feed=tempfeed)

        db.session.add(ins)
        db.session.commit()

    return render_template('contact.html')

# Route for category selection....
@app.route('/info')
def info():
    return render_template('category.html')

if __name__ == "__main__":
    app.run(debug=True)