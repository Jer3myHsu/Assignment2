import sqlite3
from flask import Flask, render_template, request, g, make_response, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from urllib.parse import urlparse, urljoin

import sys ### THIS IS FOR DEBUGGING. REMOVE

DATABASE = "./assignment3.db"
STRING_LIMIT = 30
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///assignment3.db"
app.config['SECRET_KEY'] = '1jhhgf'
app.config['USE_SESSION_FOR_NEXT'] = True
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

class User:
    id = 0
    is_instructor = False

# From https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
def get_db():
    db=getattr(g,'_database', None)
    if db is None:
        db=g._database=sqlite3.connect(DATABASE)
    return db

# From https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# From https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# From https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(STRING_LIMIT), unique=True)
    password = db.Column(db.String(STRING_LIMIT))
    name = db.Column(db.String(STRING_LIMIT))

class Instructor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(STRING_LIMIT), unique=True)
    password = db.Column(db.String(STRING_LIMIT))
    name = db.Column(db.String(STRING_LIMIT))
    role = db.Column(db.String(STRING_LIMIT))
    email = db.Column(db.String(STRING_LIMIT))

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        checkbox = request.form.get('checkbox')
        if checkbox == 'on':
            user = Instructor.query.filter_by(username=username).first()
        else:
            user = Student.query.filter_by(username=username).first()
        if not user: # User DNE
            return redirect('/login')
        if checkbox == 'on':
            user = Instructor.query.filter_by(username=username, password=password).first()
        else:
            user = Student.query.filter_by(username=username, password=password).first()
        if not user: # Password incorrect
            return redirect('/login')
        login_user(user)
        #if 'next' in session:
        #    next = session['next']
        #    return redirect(next)
        User.id = user.id
        User.is_instructor = checkbox == 'on'
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    User.id = 0
    User.is_instructor = False
    return 'Logged Out'

@app.route('/')
@login_required
def root():
    return render_template('index.html')

@app.route('/assignment')
@login_required
def assignment_page():
    return render_template('assignment.html')

@app.route('/calendar')
@login_required
def calendar_page():
    return render_template('calendar.html')

@app.route('/feedback')
@login_required
def feedback_page():
    return render_template('feedback.html')

@app.route('/labs')
@login_required
def labs_page():
    return render_template('labs.html')

@app.route('/lectures')
@login_required
def lectures_page():
    return render_template('lectures.html')

@app.route('/resources')
@login_required
def resources_page():
    return render_template('resources.html')

@app.route('/instructor_grades')
@login_required
def instructor_grades_page():
    if User.is_instructor:
        db = get_db()
        db.row_factory = make_dicts
        grades = []
        for grade in query_db('select * from Grades'):
            grades.append(grade)
        db.close()
        return render_template('instructor_grades.html', grade=grades)
    else:
        db = get_db()
        db.row_factory = make_dicts
        grades = []
        for grade in query_db('select * from Grades where Grades.sid == ' + str(User.id)):
            grades.append(grade)
        db.close()
        return render_template('instructor_grades.html', grade=grades)

@app.route('/team')
@login_required
def team_page():
    db = get_db()
    db.row_factory = make_dicts
    instructors = []
    for instructor in query_db('select * from Instructor'):
        instructors.append(instructor)
    db.close()
    return render_template('team.html', instructor=instructors)

@app.route('/<incorrect>')
def incorrect_url(incorrect):
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)#,host='0.0.0.0')