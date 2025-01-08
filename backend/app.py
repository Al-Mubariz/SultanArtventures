from flask import Flask, request, session
import sqlite3
import hashlib

con = sqlite3.connect("db/game.db", check_same_thread=False)

app = Flask(__name__)
app.secret_key = 'E.q.e4{IFu_sG5VN5mKa9*'

def sha256_hash(value):
    if value is not None:
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    return None


def create_account(username, password):
    rows = con.execute("SELECT * from users").fetchall()
    for row in rows:
        if row[1] == username:
            return False

    rows = con.execute("INSERT INTO users(username, password) VALUES(?, ?)", [username, sha256_hash(password)])
    con.commit()
    
    return True


def valid_login(username, password):
    row = con.execute("SELECT password from users as u where u.username == ?", [username]).fetchall()
    print(len(row))
    if len(row) > 0:
        if row[0][0] == sha256_hash(password):
            return True
    return False



def get_level(username):
    row = con.execute("SELECT levels from users as u where u.username == ?", [username]).fetchall()
    return row[0][0]



@app.route('/login', methods=['POST'])
def login():
    error = None
    if "username" not in request.form or "password" not in request.form:
        return {"error":"You must enter a username and a password"}, 403
    if valid_login(request.form['username'], request.form['password']):
        session["username"] = request.form["username"]
        session["authenticated"] = True
        return {"level":get_level(request.form['username'])}, 200
    else:
       error = 'Invalid username/password'
    

@app.route("/register", methods=["POST"])
def register():
    if "username" not in request.form or "password" not in request.form:
        return {"error":"You must enter a username and a password"}, 403
    errc = create_account(request.form["username"], request.form["password"])
    if errc == False:
        return {"error":"This username is already taken."}, 200
    else:
        session["username"] = request.form["username"]
        session["authenticated"] = True
        return {"msg":"Account successfully created."}, 200

@app.route("/levels", methods=["GET","POST"])
def solve_level():
    if request.method == "POST":
        if "authenticated" in session == True:
            if get_level(session["username"]) >= 5:
                return {"error":"You are already at the last level."}, 200
            row = con.execute("UPDATE users SET levels = levels + 1 WHERE username=?", [session["username"]])
            con.commit()
            return {"level":get_level(request.form['username'])}, 200
        else:
            return {"error":"You are not authenticated."}

    elif request.method == "GET":
        if "authenticated" in session == True:
            return {"level":get_level(session["username"])},200
