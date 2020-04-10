import sqlite3
from flask import Flask, render_template, request, g, make_response, redirect, session, flash

DATABASE = "./assignment3.db"
STRING_LIMIT = 30
app = Flask(__name__)
app.config['SECRET_KEY'] = 'vN0JyIeUzvGi6VYMgmtdUqNkf6XzUEdx'
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

def get_name():
    db = get_db()
    db.row_factory = make_dicts
    name = query_db("select name from Instructor where username == '{}'\
        union select name from Student where username == '{}'".format(session['username'] , session['username']), one=True)
    db.close()
    return [name]

def get_account_items():
    if session['type'] == 'instructor':
        return [{'link': 'grades', 'text': 'Student Grades'}, {'link': 'remark', 'text': 'Remark Requests'},
            {'link': 'feedback', 'text': 'Your Feedback'}, {'link': 'logout', 'text': 'Log out'}]
    else:
        return [{'link': 'grades', 'text': 'Your Grades'}, {'link': 'remark', 'text': 'Request Remark'},
            {'link': 'feedback', 'text': 'Feedback'}, {'link': 'logout', 'text': 'Log out'}]

def check_login(page):
    return render_template(page) if 'username' in session else redirect('/login')

@app.route('/navigation')
def navigation():
    return render_template('navigation.html', name=get_name(), list=get_account_items()) if 'username' in session else ''

@app.route('/footer')
def footer():
    return render_template('footer.html')

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
            user = query_db("select * from Instructor where username == '{}'".format(username), one=True)
        else:
            user = query_db("select * from Student where username == '{}'".format(username), one=True)
        if user:
            flash('\U000026D4 Username is taken') # \U000026D4 is ⛔ (no entry emoji)
            error = True
        if email == '':
            flash('\U000026D4 Email cannot be empty')
            error = True
        if name == '':
            flash('\U000026D4 Name cannot be empty')
            error = True
        if username == '':
            flash('\U000026D4 Username cannot be empty')
            error = True
        if password != confirm_password:
            flash('\U000026D4 Password does not match')
            error = True
        if password == '':
            flash('\U000026D4 Password cannot be empty')
            error = True
        if error:
            return redirect('/signup')
        if checkbox == 'on':
            role = request.form['role']
            if role == '':
                role = 'Teaching Assistant'
            query_db("insert into Instructor (username, password, name, role, email)\
                values ('{}','{}','{}','{}', '{}')".format(username, password, name, role, email))
        else:
            query_db("insert into Student(username, password, name, email)\
                values ('{}','{}','{}','{}')".format(username, password, name, email))
        db.commit()
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
            user = query_db("select * from Instructor where username == '{}'".format(username), one=True)
        else:
            user = query_db("select * from Student where username == '{}'".format(username), one=True)
        if not user:
            flash('\U000026D4 Incorrect username...')
            return redirect('/login')
        if checkbox == 'on':
            user = query_db("select * from Instructor where username == '{}' and password == '{}'".format(username, password), one=True)
        else:
            user = query_db("select * from Student where username == '{}' and password == '{}'".format(username, password), one=True)
        if not user:
            flash('\U000026D4 Incorrect password...')
            return redirect('/login')
        db.close()
        session['username'] = username
        session['type'] = 'instructor' if checkbox == 'on' else 'student'
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

@app.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    if 'username' in session:
        db = get_db()
        db.row_factory = make_dicts
        if session['type'] == 'instructor':
            feedbacks = []
            for feedback in query_db("select * from Feedback F, Instructor I where F.username == I.username\
                and I.username == '{}'".format(session['username'])):
                feedbacks.append(feedback)
            if feedbacks == []:
                flash('You have no Feedback...')
            db.close()
            return render_template('instructor_feedback.html', feedback=feedbacks)
        else:
            if request.method == 'POST':
                instructor = request.form['instructor_list']
                q_a = request.form['q_a']
                q_b = request.form['q_b']
                q_c = request.form['q_c']
                q_d = request.form['q_d']
                email_checkbox = request.form.get('email_checkbox')
                if q_a.strip() == '' and q_b.strip() == '' and q_c.strip() == '' and q_d.strip() == '':
                    flash('There is no message to send...')
                    return redirect('/feedback')
                if email_checkbox == 'on':
                    email = query_db("select email from Student where username == '{}'".format(session['username']), one=True)['s_email']
                    query_db("insert into Feedback(username, s_email, q_a, q_b, q_c, q_d)\
                        values ('{}','{}','{}','{}','{}','{}')".format(instructor, email, q_a, q_b, q_c, q_d))
                else:
                    query_db("insert into Feedback(username, q_a, q_b, q_c, q_d)\
                        values ('{}','{}','{}','{}','{}')".format(instructor, q_a, q_b, q_c, q_d))
                db.commit()
                db.close()
                flash('Submitted Successfully!')
                return redirect('/feedback')
            else:
                instructors = []
                for instructor in query_db('select * from Instructor'):
                    instructors.append(instructor)
                db.close()
                return render_template('student_feedback.html', instructor=instructors) 
    else:
        return redirect('/login')

@app.route('/labs')
def labs_page():
    return check_login('labs.html')

@app.route('/lectures')
def lectures_page():
    return check_login('lectures.html')

@app.route('/resources')
def resources_page():
    return check_login('resources.html')

@app.route('/grades', methods=['GET', 'POST'])
def grades_page():
    if 'username' in session:
        db = get_db()
        db.row_factory = make_dicts
        if session['type'] == 'instructor':
            if request.method == 'POST':
                button = request.form['button']
                if button == 'Add':
                    username = request.form['name']
                    assignment = request.form['assignment']
                    grade = request.form['grade']
                    if grade == '':
                        grade = 0
                    check = query_db("select * from Grades where username == '{}'\
                        and assignment == '{}'".format(username, assignment), one=True)
                    if check:
                        query_db("update Grades set grade = '{}' where username == '{}'\
                            and assignment == '{}'".format(grade, username, assignment))
                        flash('Grade Already Exist so it has been changed')
                    else:
                        query_db("insert into Grades(username, assignment, grade)\
                            values ('{}','{}','{}') ".format(username, assignment, grade))
                        flash('Added Successfully!')
                    db.commit()
                elif button == 'Update':
                    old_grades = query_db("select * from Grades")
                    for grade in old_grades:
                        new_grade = request.form[str(grade['id'])]
                        # grade['id'] = grade id
                        # grade['grade'] = current grade
                        if new_grade == '':
                            new_grade = 0
                        if new_grade != grade['grade']:
                            query_db("update Grades set grade = '{}' where id == '{}'".format(new_grade, grade['id']))
                            db.commit()
                    flash('Updated Successfully!')
                db.close()
                return redirect('grades')
            else:
                grades = []
                students = []
                for grade in query_db('select * from Grades G, Student S where G.username == S.username'):
                    grades.append(grade)
                for student in query_db('select * from Student'):
                    students.append(student)
                db.close()
                return render_template('instructor_grades.html', grade=grades, student=students)
        else:
            grades = []
            for grade in query_db('''select * from  Grades G, Student S where G.username == S.username
                and G.username == '{}' '''.format(session['username'])):
                grades.append(grade)
            if grades == []:
                flash('No grades available yet...')
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

@app.route('/remark', methods=['GET', 'POST'])
def remark_page():
    if 'username' in session:
        db = get_db()
        db.row_factory = make_dicts
        if session['type'] == 'instructor':
            if request.method == 'POST':
                name = request.form['name']
                remarks = []
                if name.strip() == '':
                    for remark in query_db('select reason, name, assignment from\
                        (select * from Remark R, Grades G where R.grade_id == G.id) A, Student S\
                        where A.username == S.username'):
                        remarks.append(remark)
                    db.close()
                    return render_template('instructor_remark.html', remark=remarks)
                else:    
                    for remark in query_db('''select reason, name, assignment from\
                        (select * from Remark R, Grades G where R.grade_id == G.id) A, Student S\
                        where A.username == S.username and S.name == '{}' '''.format(name)):
                        remarks.append(remark)
                    db.close()
                    return render_template('instructor_remark.html', remark=remarks)
            else:
                remarks = []
                for remark in query_db('select reason, name, assignment from\
                        (select * from Remark R, Grades G where R.grade_id == G.id) A, Student S\
                        where A.username == S.username'):
                    remarks.append(remark)
                db.close()
                return render_template('instructor_remark.html', remark=remarks)
        else:
            if request.method == 'POST':
                grade_id = request.form['grade_id']
                reason = request.form['reason']
                if grade_id == 'None':
                    flash("Assignment doesn't exist")
                    return redirect('remark')
                if reason.strip() == '':
                    flash("You have not entered a reason for your remark")
                    return redirect('remark')
                query_db("insert into Remark (grade_id, reason)\
                values ('{}','{}')".format(grade_id, reason))
                db.commit()
                db.close()
                flash('Submitted Successfully!')
                return redirect('remark')
            else:
                assignments = []
                for assignment in query_db("select * from Grades where username == '{}'".format(session['username'])):
                    assignments.append(assignment)
                db.close()
                if assignments == []:
                    assignments.append({'id': None, 'assignment': 'No assignments found'})
                return render_template('student_remark.html', assignment=assignments)    
    else:
        return redirect('/login')

@app.errorhandler(404)
def incorrect_url(incorrect):
    return render_template('/not_found.html'), 404

if __name__ == '__main__':
    app.run(debug=True)#,host='0.0.0.0')