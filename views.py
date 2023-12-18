
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

def calculate_remaining_time(pre_time,lev_time):
    cur_time = 90 - int(lev_time)
    return pre_time + cur_time

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
        session['quiz_time'] = 0 
    if 'quiz_level_passed' not in session:
        session['quiz_level_passed'] = 1

    if session['quiz_level_passed'] > level:
        # print(session['quiz_level_passed'])
        return redirect(url_for('quiz', name=name,level=session['quiz_level_passed']))

    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions WHERE level=? ORDER BY question',(level_title,))
    questions = questions.fetchall()
    question_lev=int(level)
    

    session['quiz_level_passed']=level

    if request.method == 'POST':
        lev_time = request.form["remaining_time"]
        print(lev_time)
        print(session['quiz_time'])
        session['quiz_time'] = calculate_remaining_time(session['quiz_time'], lev_time)
        print(session['quiz_time'])

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
            session['quiz_time'] = calculate_remaining_time(session['quiz_time'], lev_time)
            quizid=session['quiz_id']
            result= conn.execute('SELECT sum(mark_count) as total_mark FROM user_answers WHERE quiz_id=? and user_id=?',(quizid,session['user_id'],))
            total_mark=result.fetchone()[0]

            time_format =0 
            hours, remainder = divmod(session['quiz_time'], 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = f"{int(minutes)}:{int(seconds)}"
            
            cursor = conn.cursor()
            cursor.execute('INSERT INTO quiz_list (quiz_id, user_id, total_mark, category) VALUES (?, ?, ?, ?)', (quizid, session['user_id'],total_mark, time_format))
            conn.commit() 
            session.pop('quiz_id')
            session.pop('quiz_level_passed')
            session.pop('quiz_time')
            flash('Thank you. You are successful complete!')
            return redirect(url_for('profile'))
        if int(level) >= 6:
            session.pop('quiz_id')
            session.pop('quiz_level_passed')
            session.pop('quiz_time')
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

def is_admin():
    return session.get('user_type')

@app.route('/leaderboard')
def leaderboard():
    if not is_admin():
        return redirect(url_for('hello'))
    if 'user_id' in session:
        conn = get_db_connection()
        category_cursor = conn.execute('SELECT category_id FROM tutorials GROUP BY category_id ')
        categories = category_cursor.fetchall()    

        quiz_cat = request.args.get('quiz_cat')
        quiz_details=''
        if quiz_cat:
           # Assuming you have quiz_details defined
            quiz_details = conn.execute(
                'SELECT * FROM quiz_list JOIN users ON users.id = quiz_list.user_id WHERE quiz_list.category = ? ORDER BY total_mark DESC, category ASC',
                (quiz_cat,)
            ).fetchall()
        else:
            quiz_details = conn.execute(
                'SELECT * FROM quiz_list JOIN users ON users.id = quiz_list.user_id ORDER BY total_mark DESC, category ASC',
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

# @app.route('/test')
# def test():
    
#     conn = get_db_connection()
#     category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ')
#     categories = category_cursor.fetchall()    
#     conn.close()

#     return render_template('tuto.html',name=name,levels=levels_data)


# @app.route('/mi')
# def mi():
    
#     conn = get_db_connection()
#     category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ')
#     categories = category_cursor.fetchall()    
#     conn.close()

#     return "image view area"


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

def load_nii(filepath):
    img = nib.load(filepath)
    data = img.get_fdata()
    return data

import tempfile
import plotly.graph_objs as go
def plot_slices(nii_data, plane):
    if plane == "Axial":
        fig = px.imshow(nii_data[:, :, nii_data.shape[2]//2].T, color_continuous_scale='gray')
    elif plane == "Sagittal":
        fig = px.imshow(nii_data[:, nii_data.shape[1]//2, :].T, color_continuous_scale='gray')

    elif plane == "Coronal":
        fig = px.imshow(nii_data[nii_data.shape[0]//2, :, :].T, color_continuous_scale='gray')
    
    fig.update_layout(title=f"{plane} Plane")
    fig.update_xaxes(title_text="Coronal")
    fig.update_yaxes(title_text="Sagittal")

    # Save the plot to a temporary HTML file
    temp_dir = tempfile.mkdtemp()
    plot_html_path = os.path.join('static', f'{plane.lower()}_plot.html')
    fig.write_html(plot_html_path)

    return plot_html_path


@app.route('/view_imgd')
def img_view():
    image_id = request.args.get('image_id')
    path = app.static_folder + "/uploads/"
    nii_file_path = str(path) + str(image_id)
    
    nii_data = load_nii(nii_file_path)
# # Create axial, sagittal, and coronal plots
#     axial_plot = px.imshow(nii_data[:, :, nii_data.shape[2]//2].T, binary_string=True)
#     sagittal_plot = px.imshow(nii_data[:, nii_data.shape[1]//2, :].T, binary_string=True)
#     coronal_plot = px.imshow(nii_data[nii_data.shape[0]//2, :, :].T, binary_string=True)

    # # Create 3D visualization
    # combined_fig = plot_3d_visualization(nii_data)

    # # Save plots as temporary HTML files
    # temp_dir = tempfile.mkdtemp()
    # axial_html_path = os.path.join(temp_dir, 'axial_plot.html')
    # sagittal_html_path = os.path.join(temp_dir, 'sagittal_plot.html')
    # coronal_html_path = os.path.join(temp_dir, 'coronal_plot.html')
    # combined_html_path = os.path.join(temp_dir, 'combined_plot.html')

    # axial_plot.write_html(axial_html_path)
    # sagittal_plot.write_html(sagittal_html_path)
    # coronal_plot.write_html(coronal_html_path)
    # combined_fig.write_html(combined_html_path)

    # return render_template('view3d.html', axial_plot=axial_html_path, sagittal_plot=sagittal_html_path, coronal_plot=coronal_html_path, combined_plot=combined_html_path)
    # Create and save axial, sagittal, and coronal plots
    # Create and save axial, sagittal, and coronal plots
    axial_plot = plot_slices(nii_data, "Axial")
    sagittal_plot = plot_slices(nii_data, "Sagittal")
    coronal_plot = plot_slices(nii_data, "Coronal")


    return render_template('view3d.html', axial_plot=axial_plot, sagittal_plot=sagittal_plot, coronal_plot=coronal_plot)
