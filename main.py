from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import sqlite3
from datetime import datetime
import re

# db setup
db = sqlite3.connect('kanban.db') # kanban.db is the filename
cursor = db.cursor() # create a cursor object
cursor.execute('CREATE TABLE IF NOT EXISTS users (\
ID INTEGER PRIMARY KEY AUTOINCREMENT, \
USERNAME TEXT NOT NULL, \
PASSWORD TEXT NOT NULL)')

cursor.execute('CREATE TABLE IF NOT EXISTS lists (\
ID INTEGER PRIMARY KEY AUTOINCREMENT, \
USERID INTEGER NOT NULL, \
TITLE TEXT NOT NULL, \
FOREIGN KEY(USERID) REFERENCES users(ID))')

cursor.execute('CREATE TABLE IF NOT EXISTS cards (\
ID INTEGER PRIMARY KEY AUTOINCREMENT, \
LISTID INTEGER NOT NULL, \
TITLE TEXT NOT NULL, \
CONTENT TEXT NOT NULL, \
DEADLINE DATETIME NOT NULL, \
COMPLETED INTEGER NOT NULL, \
CREATED_AT DATETIME NOT NULL, \
LAST_MODIFIED DATETIME NOT NULL, \
COMPLETED_AT DATETIME, \
FOREIGN KEY(LISTID) REFERENCES lists(ID))')

db.commit() # save changes
db.close()

app = Flask(__name__)
app.secret_key = "Secret_Key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
Session(app)

# function for using db in flask
def sql(cmd, vals=None):
  conn = sqlite3.connect('kanban.db')
  cur = conn.cursor()
  res = cur.execute(cmd, vals).fetchall()
  conn.commit()
  conn.close()
  return res

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/signup', methods = ['POST'])
def signup():
  if request.method == 'POST':
    password = request.form['password']
    username = request.form['username']
    
    result = re.match('^[A-Za-z0-9]$', password)
    
    if not username:
      flash("Username can not be empty.")
    else:
      if len(password) < 8 and not result:
        flash("Your password must be atleast 8 characters long and contain letters & numbers.")
      else:
        if password == request.form['confirm-password']:
          sql('INSERT INTO users (USERNAME, PASSWORD) VALUES (?, ?)', (
            username,
            password,
          ))
          flash("Account Created Successfully")
        else:
          flash("Passwords do not match. Try Again!")
    return redirect(url_for('index'))

@app.route('/login', methods = ['POST'])
def login():
  if request.method == 'POST':
    userid = sql('SELECT ID FROM users WHERE USERNAME=? AND PASSWORD=?', (
      request.form['username'],
      request.form['password'],
    ))
    if userid:
      session['userid'] = userid[0][0]
      return redirect(url_for('dashboard'))
    else:
      flash("Username or Password is Incorrect")
      return redirect(url_for('index'))

@app.route('/logout', methods = ['GET'])
def logout():
  session["userid"] = None
  flash("Logged Out Successfully")
  return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
  if 'userid' not in session:
    return redirect(url_for('index'))
  userid = session['userid']
  conn = sqlite3.connect('kanban.db')
  cur = conn.cursor()
  all_lists = cur.execute('SELECT * FROM lists WHERE USERID=?', str(userid)).fetchall()
  all_cards = cur.execute('SELECT * FROM cards').fetchall()
  conn.commit()
  conn.close()
  return render_template("dashboard.html", lists=all_lists, cards=all_cards, userid=userid)

@app.route('/addlist/<uid>', methods = ['POST'])
def addlist(uid):
  if request.method == 'POST':
    sql('INSERT INTO lists (USERID, TITLE) VALUES (?, ?)', (
      uid,
      request.form['title'],
    ))
    return redirect(url_for('dashboard'))

@app.route('/editlist/<id>', methods = ['GET', 'POST'])
def editlist(id):
  if request.method == 'POST':
    sql('UPDATE lists SET TITLE=? WHERE ID=?', (
      request.form['title'],
      id,
    ))
    return redirect(url_for('dashboard'))

@app.route('/deletelist/<id>', methods = ['GET'])
def deletelist(id):
  sql('DELETE FROM lists WHERE ID=?', (
    id,
  ))
  return redirect(url_for('dashboard'))

@app.route('/addcard/<lid>', methods = ['POST'])
def addcard(lid):
  if request.method == 'POST':
    sql('INSERT INTO cards (LISTID, TITLE, CONTENT, DEADLINE, COMPLETED, CREATED_AT, LAST_MODIFIED) VALUES (?, ?, ?, ?, ?, ?, ?)', (
      lid,
      request.form['title'],
      request.form['content'],
      request.form['deadline'],
      0,
      datetime.now(),
      datetime.now(),
    ))
    return redirect(url_for('dashboard'))

@app.route('/editcard/<id>', methods = ['GET', 'POST'])
def editcard(id):
  if request.method == 'POST':
    sql('UPDATE cards SET TITLE=?, CONTENT=?, DEADLINE=?, LAST_MODIFIED=? WHERE ID=?', (
      request.form['title'],
      request.form['content'],
      request.form['deadline'],
      datetime.now(),
      id,
    ))
    return redirect(url_for('dashboard'))

@app.route('/movecard/<id>', methods = ['GET', 'POST'])
def movecard(id):
  if request.method == 'POST':
    sql('UPDATE cards SET LISTID=?, LAST_MODIFIED=? WHERE ID=?', (
      request.form['lid'],
      datetime.now(),
      id,
    ))
    return redirect(url_for('dashboard'))

@app.route('/completed', methods = ['GET'])
def completed():
  id = request.args.get('id', 0)
  value = request.args.get('value', 0)
  print(value)
  if value == '1':
    sql('UPDATE cards SET COMPLETED=?, LAST_MODIFIED=?, COMPLETED_AT=? WHERE ID=?', (
      value,
      datetime.now(),
      datetime.now(),
      id,
    ))
  else:
    sql('UPDATE cards SET COMPLETED=?, LAST_MODIFIED=? WHERE ID=?', (
      value,
      datetime.now(),
      id,
    ))
  return redirect(url_for('dashboard'))

@app.route('/deletecard/<id>', methods = ['GET'])
def deletecard(id):
  sql('DELETE FROM cards WHERE ID=?', (
    id,
  ))
  return redirect(url_for('dashboard'))

@app.route('/summary')
def summary():
  if 'userid' not in session:
    return redirect(url_for('index'))
  userid = session['userid']
  conn = sqlite3.connect('kanban.db')
  cur = conn.cursor()
  all_lists = cur.execute('SELECT * FROM lists WHERE USERID=?', str(userid)).fetchall()
  all_cards = cur.execute('SELECT * FROM cards').fetchall()
  conn.commit()
  conn.close()
  return render_template("summary.html", lists = all_lists, cards = all_cards)

@app.route('/carddata', methods = ['GET'])
def carddata():
  conn = sqlite3.connect('kanban.db')
  cur = conn.cursor()
  cards = cur.execute('SELECT * FROM cards').fetchall()
  conn.commit()
  conn.close()
  return cards

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81)
