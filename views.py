
# views.py

import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from app import app

mail = Mail(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def hello():
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()
    conn.close()
    return render_template('index.html', categories=categories, utc_dt=datetime.datetime.utcnow())

@app.route('/tutorial')
def tutorial():
    
    conn = get_db_connection()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    conn.close()

    return render_template('tutorial.html',categories=categories,)


@app.route('/tuto',defaults={'name':"MRI"})
@app.route('/tuto/<name>')
def tuto(name):
    name = request.args.get('category')
    conn = get_db_connection()
    levels_cursor = conn.execute('SELECT level_id, title, description, details FROM tutorials WHERE category_id=? ORDER BY title',(name,))
    levels=levels_cursor.fetchall()
    category_cursor = conn.execute('SELECT category_id, description AS total_quantity FROM tutorials GROUP BY category_id ')
    categories = category_cursor.fetchall()    
    conn.close()

    return render_template('tuto.html',name=name,levels=levels,categories=categories)

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
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchall()
        conn.close()
        return render_template('profile.html',user=user)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
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

