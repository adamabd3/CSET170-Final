from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import *

app = Flask(__name__)
conn_str = "mysql://root:1234@localhost/sfcu"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


users = {}
@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')
# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users[username] = {'password': password}
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            # Authentication successful, redirect to user's dashboard
            return redirect(url_for('dashboard', username=username))
        else:
            return "Invalid username or password"
    return render_template('user.html')

# Route for user dashboard
@app.route('/dashboard/<username>')
def dashboard(username):
    # Placeholder for user dashboard, you can render user-specific data here
    return f"Welcome {username} to your dashboard"

if __name__ == '__main__':
    app.run(debug=True)
