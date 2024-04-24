from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/sfcu'
db = SQLAlchemy(app)
app.secret_key = 'shhhh'


class Users(db.Model):
    username = db.Column(db.String(50), unique=True, primary_key=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    ssn = db.Column(db.String(100), unique=True)
    address = db.Column(db.String(255))
    phonenumber = db.Column(db.String(20))
    password = db.Column(db.String(100))
    status = db.Column(db.Enum('pending', 'accepted'))
    bank_num = db.Column(db.String(10))
    money = db.Column(db.Integer)


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), primary_key=True)
    transaction_type = db.Column(db.String(10))
    amount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())




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

        new_user = Users(username=username, firstname=firstname, lastname=lastname,
                         ssn=ssn, address=address, phonenumber=phonenumber, password=password, status='pending')
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return "Error: " + str(e)
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['username'] = 'admin'
            return redirect(url_for('admin'))
        else:
            user = Users.query.filter_by(username=username, password=password).first()
        if user:
            if user.status == 'accepted':
                session['logged_in'] = True
                session['username'] = user.username
                return redirect(url_for('dashboard'))
            else:
                error = 'Account is not verified yet'
                return render_template('user.html', error=error)
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('user.html', error=error)
    return render_template('user.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('login')


@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        username = session['username']
        user = Users.query.filter_by(username=username).first()
        if user:
            transactions = Transactions.query.filter_by(username=username).all()
            print("Transactions:", transactions)  # Debug print statement
            return render_template('dashboard.html', bank_num=user.bank_num, user=user, transactions=transactions)
        else:
            return "User not found"
    else:
        return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if 'accept' in request.form:
            username = request.form['accept']
            user = Users.query.filter_by(username=username).first()
            if user:
                user.status = 'accepted'
                user.bank_num = generate_random_account_number()
                db.session.commit()
                return redirect(url_for('admin'))
            else:
                return "User not found"
    else:
        pending = Users.query.filter_by(status='pending').all()
        return render_template('admin.html', pending=pending)


def generate_random_account_number():
    return ''.join(str(random.randint(0, 9)) for _ in range(10))


@app.route('/add_funds', methods=['POST'])
def add_funds():
    if 'logged_in' in session:
        username = session['username']
        user = Users.query.filter_by(username=username).first()
        if Users:
            amount = int(request.form['amount'])
            new_transaction = Transactions(username=username, transaction_type='Deposit', amount=amount)
            credit_card = request.form['credit_card']
            user.money += amount
            db.session.add(new_transaction)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return "User not found"
    else:
        return redirect(url_for('login'))


@app.route('/withdraw_funds', methods=['POST'])
def withdraw_funds():
    if 'logged_in' in session:
        username = session['username']
        user = Users.query.filter_by(username=username).first()
        if user:
            withdraw_type = request.form['withdraw_type']
            amount = int(request.form['withdraw_amount'])
            if amount > user.money:
                return "Insufficient funds"
            user.money -= amount
            new_transaction = Transactions(username=username, transaction_type='Withdrawal', amount=amount)
            db.session.add(new_transaction)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return "User not found"
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
