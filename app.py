import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = '*z*3$ufo0i=fg+7el)7tcrpzgxa=qvins6p2(ni0x8x@k7)8e'

app.config['MAIL_SERVER'] = 'smtp.google.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''



from admin import * 
from views import * 

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='192.168.95.41', port=5000, debug=True)

