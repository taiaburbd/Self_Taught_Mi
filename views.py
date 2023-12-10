
# views.py

import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from app import app
import secrets
import os
import plotly.express as px
import nibabel as nib
import numpy as np


mail = Mail(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def hello():
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ORDER BY tutorial_id ASC')
    categories = category_cursor.fetchall()
    conn.close()
    return render_template('index.html', categories=categories, utc_dt=datetime.datetime.utcnow())

@app.route('/tutorial')
def tutorial():
    
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ORDER BY tutorial_id ASC')
    categories = category_cursor.fetchall()    
    conn.close()

    return render_template('tutorial.html',categories=categories,)


@app.route('/tuto',defaults={'name':"MRI"})
def tuto(name):
    name = request.args.get('category')
    conn = get_db_connection()
    levels_cursor = conn.execute('SELECT level_id, title, description, details FROM tutorials WHERE category_id=? ORDER BY tutorial_id desc',(name,))
    levels=levels_cursor.fetchall()
    category_cursor = conn.execute('SELECT category_id FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    conn.close()

    return render_template('tuto.html',name=name,levels=levels,categories=categories)


@app.route('/test')
def testarea():
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    conn.close()

    return render_template('test.html',categories=categories)

@app.route('/test_mi',defaults={'name':"MRI"})
def test_mi(name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = request.args.get('category')
    conn = get_db_connection()
    levels_cursor = conn.execute('SELECT level_id, title, description, details FROM tutorials WHERE category_id=? ORDER BY title',(name,))
    levels=levels_cursor.fetchall()
    category_cursor = conn.execute('SELECT category_id FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    steps=['Easy','Moderate','Challenging','Difficult','Expert']
    conn.close()

    return render_template('test_mi.html',name=name,levels=levels,categories=categories,steps=steps)

# @app.before_request
# def go_to_login():
#     if not is_login():
#         return redirect(url_for('hello'))
    
@app.route('/quiz',methods=['GET', 'POST'])
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = request.args.get('name')
    level = request.args.get('level')
    level = int(level)
    level_title = make_level_title(level)
    # generate exam id 
    if 'quiz_id' not in session:
        session['quiz_id'] = secrets.token_urlsafe(12)
    if 'quiz_level_passed' not in session:
        session['quiz_level_passed'] = 1

    if session['quiz_level_passed'] > level:
        print(session['quiz_level_passed'])
        return redirect(url_for('quiz', name=name,level=session['quiz_level_passed']))

    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions WHERE level=? ORDER BY question',(level_title,))
    questions = questions.fetchall()
    question_lev=int(level)
    

    session['quiz_level_passed']=level

    if request.method == 'POST':
        if int(level)  != 1:
            question_lev = int(level)  - 1; 
            question_lev_title = make_level_title(question_lev)
        lev_questions = conn.execute('SELECT * FROM questions WHERE level=? ORDER BY question',(question_lev_title,))
        lev_questions = lev_questions.fetchall()
        for q in lev_questions:
            user_answer = request.form.get(f'{q["id"]}')
            q_id=q['id']
            mark_count= 0
            if(user_answer == q['answer']):
                mark_count= 1
            cursor = conn.cursor()
            cursor.execute('INSERT INTO user_answers (quiz_id, user_id, question_id, user_answer, mark_count) VALUES (?, ?, ?, ?, ?)', (session['quiz_id'], session['user_id'],q_id,user_answer,mark_count))
            conn.commit()
            
        if int(level) == 5:
            
            quizid=session['quiz_id']
            result= conn.execute('SELECT sum(mark_count) as total_mark FROM user_answers WHERE quiz_id=? and user_id=?',(quizid,session['user_id'],))
            total_mark=result.fetchone()[0]

            cursor = conn.cursor()
            cursor.execute('INSERT INTO quiz_list (quiz_id, user_id, total_mark) VALUES (?, ?, ?)', (quizid, session['user_id'],total_mark))
            conn.commit()
            session.pop('quiz_id')
            session.pop('quiz_level_passed')
            flash('Thank you. You are successful complete!')
            return redirect(url_for('profile'))

    conn.close()

    return render_template('quiz.html',name=name,level=level,questions=questions)

def make_level_title(level):
    return 'Level ' + str(level)

@app.route('/visualize-mi')
def visualize_mi():
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ORDER BY tutorial_id ASC')
    categories = category_cursor.fetchall()    
    conn.close()
    return render_template('visualize.html',categories=categories)

@app.route('/visual-mi',defaults={'name':"MRI"})
def visual_mi(name):
    name = request.args.get('category')
    conn = get_db_connection()

    levels_cursor = conn.execute('SELECT * FROM images_table WHERE category=? ORDER BY id desc',(name,))
    levels=levels_cursor.fetchall()

    category_cursor = conn.execute('SELECT category_id FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    conn.close()

    return render_template('visual.html',name=name,levels=levels,categories=categories)


#auth area start
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':   
        try:
            fullname = request.form['fullname']
            username = request.form['username']
            password = request.form['password']
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (fullname, username, password) VALUES (?, ?, ?)', (fullname, username, password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.','success')
            # send_welcome_email(fullname, username)
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}','error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['user_id'] = user[0]
                session['user_fullname'] = user[1]
                session['user_name'] = user[2]
                session['user_type'] = user[4]
                flash('Login successful!')
                return redirect(url_for('profile'))
        except Exception as e:
            flash('Login failed. Please try again.')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/profile')
def profile():

    if 'user_id' in session:
        conn = get_db_connection()
        user_id=session['user_id']
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
        # Execute the SQL query
        score_list=conn.execute('SELECT * FROM quiz_list WHERE user_id = ?', (user_id,))
        score_list = score_list.fetchall()
        
        quiz_id = request.args.get('quiz_id')
        quiz_cat = request.args.get('quiz_cat')
        quiz_details=''
        if quiz_id: 
           # Assuming you have quiz_details defined
            quiz_details = conn.execute(
                'SELECT * FROM user_answers '
                'JOIN questions ON questions.id = user_answers.question_id '
                'WHERE quiz_id = ? AND user_id = ? '
                'ORDER BY questions.level',
                (quiz_id, session['user_id'])
            ).fetchall()

        conn.close()
        return render_template('profile.html',user=user,score_list=score_list,quiz_details=quiz_details,quiz_cat=quiz_cat)
    else:
        return redirect(url_for('login'))

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' in session:
        conn = get_db_connection()
        category_cursor = conn.execute('SELECT category_id FROM tutorials GROUP BY category_id ')
        categories = category_cursor.fetchall()    

        quiz_cat = request.args.get('quiz_cat')
        quiz_details=''
        if quiz_cat:
           # Assuming you have quiz_details defined
            quiz_details = conn.execute(
                'SELECT * FROM quiz_list JOIN users ON users.id = quiz_list.user_id WHERE quiz_list.category = ? ORDER BY total_mark',
                (quiz_cat,)
            ).fetchall()
        else:
            quiz_details = conn.execute(
                'SELECT * FROM quiz_list JOIN users ON users.id = quiz_list.user_id ORDER BY total_mark DESC',
            ).fetchall()

        conn.close()
        return render_template('leaderboard.html',quiz_details=quiz_details,quiz_cat=quiz_cat,categories=categories)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#auth area end 

@app.route('/test')
def test():
    
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    conn.close()

    return render_template('tuto.html',name=name,levels=levels_data)


@app.route('/mi')
def mi():
    
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    conn.close()

    return "image view area"


# helper function
def send_welcome_email(username, email):
    msg = Message('Thank you for registering [STMi]', sender='maia@st-mi.diqcare.com', recipients=[email])
    msg.html = render_template('email_registration.html', username=username)
    mail.send(msg)

# Logging user check
def get_login_user():
    return session.get('user_id')

def is_login():
    return 1 if get_login_user() else 0

# image views

def load_nii(file_path):
    # Load .nii file
    nii_img = nib.load(file_path)
    data = nii_img.get_fdata()
    return data

def create_plot(data):
    # Create a 3D plot using Plotly
    x, y, z = np.where(data > 0)
    values = data[x, y, z]

    fig = px.scatter_3d(x=x, y=y, z=z, color=values, opacity=0.6, size_max=6)
    fig.update_layout(scene=dict(aspectmode="data"))

    return fig

app.route('/view3d/<filename>')
def view3d(filename):
    path = app.static_folder+"/uploads/"
    nii_file_path = path + filename
    nii_data = load_nii(nii_file_path)
    plot = create_plot(nii_data)

    return render_template('view3d.html', plot=plot.to_html(full_html=False))
