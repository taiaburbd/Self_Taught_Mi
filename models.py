# app/models.py
import sqlite3
from flask import g

DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.executescript(f.read())

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def save(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)",
                       (self.username, self.email))
        db.commit()
