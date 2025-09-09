from flask import Flask,request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

#Database Configurations...
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)   
app.app_context().push()

@app.route('/', methods = ['POST','GET'])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)