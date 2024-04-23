from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/sfcu'
db = SQLAlchemy(app)

class Users(db.Model):
    username = db.Column(db.String(50), unique=True, primary_key=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    ssn = db.Column(db.String(100), unique=True)
    address = db.Column(db.String(255))
    phonenumber = db.Column(db.String(20))
    password = db.Column(db.String(100))

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        ssn = request.form['ssn']
        address = request.form['address']
        phonenumber = request.form['phonenumber']
        password = request.form['password']

        new_user = Users(username=username, firstname=firstname, lastname=lastname, ssn=ssn, address=address, phonenumber=phonenumber, password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return render_template('register.html')
        except Exception as e:
            db.session.rollback()
            return "Error: " + str(e)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            user = Users.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for('dashboard', username=username))
        else:
            return "Invalid username or password"
    return render_template('user.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    return f"Welcome {username} to your dashboard"



if __name__ == '__main__':
    app.run(debug=True)
