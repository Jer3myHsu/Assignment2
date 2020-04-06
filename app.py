import sqlite3
from flask import Flask, render_template, request, g, make_response, redirect, session, flash
#from flask_login import login_required, login_user, logout_user, current_user
from urllib.parse import urlparse, urljoin

import sys ### THIS IS FOR DEBUGGING. REMOVE

DATABASE = "./assignment3.db"
STRING_LIMIT = 30
app = Flask(__name__)
app.config['SECRET_KEY'] = '1jhhgf'
app.config['USE_SESSION_FOR_NEXT'] = True

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

def check_login(page):
    return render_template(page) if 'username' in session else redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        error = False
        email = request.form['email']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        checkbox = request.form.get('checkbox')
        db = get_db()
        db.row_factory = make_dicts
        if checkbox == 'on':
            user = query_db("select * from Instructor where username == '{}'".format(str(username)), one=True)
        else:
            user = query_db("select * from Student where username == '{}'".format(str(username)), one=True)
        if user:
            flash('\U000026D4 Username is taken')
            error = True
        if str(username) == "":
            flash('\U000026D4 Username cannot be empty')
            error = True
        if str(password) != str(confirm_password):
            flash('\U000026D4 Password does not match')
            error = True
        if str(password) == "":
            flash('\U000026D4 Password cannot be empty')
            error = True
        if error:
            return redirect('/signup')
        if checkbox == 'on':
            query_db("insert into Instructor (username, password, name, role, email)\
                values ('{}','{}','{}','{}', '{}')".format(str(username), str(password), str(name), 'Teaching Assistant', str(email)))
        else:
            query_db("insert into Student(username, password, name, email)\
                values ('{}','{}','{}','{}')".format(str(username), str(password), str(name), str(email)))
        db.close()
        return redirect('/login')
    elif 'username' in session:
        return redirect('/')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        checkbox = request.form.get('checkbox')
        db = get_db()
        db.row_factory = make_dicts
        if checkbox == 'on':
            user = query_db("select * from Instructor where username == '{}'".format(str(username)), one=True)
        else:
            user = query_db("select * from Student where username == '{}'".format(str(username)), one=True)
        if not user:
            flash('\U000026D4 Incorrect username...') # \U000026D4 is ⛔ (no entry emoji)
            return redirect('/login')
        if checkbox == 'on':
            user = query_db("select * from Instructor where username == '{}' and password == '{}'".format(str(username), str(password)), one=True)
        else:
            user = query_db("select * from Student where username == '{}' and password == '{}'".format(str(username), str(password)), one=True)
        if not user:
            flash('\U000026D4 Incorrect password...')
            return redirect('/login')
        db.close()
        session['username'] = username
        session['type'] = 'instructor' if checkbox == 'on' else 'student'
        if 'next' in session:
            next = session['next']
            return redirect(next)
        return redirect('/')
    elif 'username' in session:
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('type', None)
    return redirect('/login')

@app.route('/')
def root():
    return check_login('index.html')

@app.route('/assignment')
def assignment_page():
    return check_login('assignment.html')

@app.route('/calendar')
def calendar_page():
    return check_login('calendar.html')

@app.route('/feedback')
def feedback_page():
    return check_login('feedback.html')

@app.route('/labs')
def labs_page():
    return check_login('labs.html')

@app.route('/lectures')
def lectures_page():
    return check_login('lectures.html')

@app.route('/resources')
def resources_page():
    return check_login('resources.html')

@app.route('/grades')
def grades_page():
    if 'username' in session:
        if session['type'] == 'instructor':
            db = get_db()
            db.row_factory = make_dicts
            grades = []
            for grade in query_db('select * from Grades G, Student S where G.username == S.username'):
                grades.append(grade)
            db.close()
            return render_template('instructor_grades.html', grade=grades)
        else:
            db = get_db()
            db.row_factory = make_dicts
            grades = []
            for grade in query_db('''select * from  Grades G, Student S where G.username == S.username
                and G.username == '{}' '''.format(str(session['username']))):
                grades.append(grade)
            db.close()
            return render_template('student_grades.html', grade=grades)
    else:
        return redirect('/login')

@app.route('/team')
def team_page():
    if 'username' in session:
        db = get_db()
        db.row_factory = make_dicts
        instructors = []
        for instructor in query_db('select * from Instructor'):
            instructors.append(instructor)
        db.close()
        return render_template('team.html', instructor=instructors)
    else:
        return redirect('/login')

@app.route('/<incorrect>')
def incorrect_url(incorrect):
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)#,host='0.0.0.0')