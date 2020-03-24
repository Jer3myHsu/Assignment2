import sqlite3
from flask import Flask, render_template, request, g

app = Flask(__name__)
DATABASE = "./assignment3.db"

# https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/
def get_db():
    db=getattr(g,'_database', None)
    if db is None:
        db=g._database=sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/assignment')
def assignment_page():
    return render_template('assignment.html')

@app.route('/calendar')
def calendar_page():
    return render_template('calendar.html')

@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html')

@app.route('/labs')
def labs_page():
    return render_template('labs.html')

@app.route('/lectures')
def lectures_page():
    return render_template('lectures.html')

@app.route('/resources')
def resources_page():
    return render_template('resources.html')

@app.route('/instructor_grades')
def instructor_grades_page():
    db = get_db()
    db.row_factory = make_dicts
    grades = []
    for grade in query_db('select * from Grades'):
        grades.append(grade)
    db.close()
    return render_template('instructor_grades.html', grade=grades)

@app.route('/team')
def team_page():
    db = get_db()
    db.row_factory = make_dicts
    instructors = []
    for instructor in query_db('select * from Instructors'):
        instructors.append(instructor)
    db.close()
    return render_template('team.html', instructor=instructors)

@app.route('/login')
def login_page():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)