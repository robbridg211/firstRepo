from flask import Flask, render_template, session, request, redirect, flash
# import the function connectToMySQL from the file mysqlconnection.py
from mysqlconnection import connectToMySQL
import datetime
import re
from flask_bcrypt import Bcrypt
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'SecretsSecretsAreNoFun,SecretsSecretsHurtSomeone'
bcrypt = Bcrypt(app)
# invoke the connectToMySQL function and pass it the name of the database we're using
# connectToMySQL returns an instance of MySQLConnection, which we will store in the variable 'mysql'

def addUserToDatabase(first_name, last_name, email, password):
    pw_hash = bcrypt.generate_password_hash(request.form['password'])  
    mysql = connectToMySQL("registration")
    query = "INSERT INTO users (`first_name`,`last_name`,`email`, `password`, `created_at`, `updated_at`, `user_level`) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s, %(created_at)s, %(updated_at)s, 1 );" #val 1 makes user_level =1 by default
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password_hash": pw_hash,
        "created_at": datetime.datetime.now(),
        "updated_at" : datetime.datetime.now()
    }
    newUser = mysql.query_db(query, data)

    return newUser


def check_login():
    if 'email' not in session or session['email'] == None:
        return False
    return True

@app.route('/')
def index():
    if 'email' not in session:
        session['email'] = None
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    messages = False
                ######## first name registration validation #######
    if len(request.form['first_name']) < 1:
        flash(f"<span style='color: red'>This field required!</span>", 'first_name')
    if len(request.form['first_name']) < 2:
        messages = True
        flash(f"<span style='color: red'>First name must be 2+ characters!</span>", 'first_name')

            ######## last name registration validation #######
    if len(request.form['last_name']) < 1:
        messages = True
        flash(f"<span style='color: red'>This field required!</span>", 'last_name')
    if len(request.form['last_name']) < 2:
        messages = True
        flash(f"<span style='color: red'>Last name must be 2+ characters</span>", 'last_name')

            ######## email registration validation #######
    if len(request.form['email']) < 1:
        messages = True
        flash(f"<span style='color: red'>This field required!</span>", 'email')
    if not EMAIL_REGEX.match(request.form['email']):
        messages = True
        flash(f"<span style='color: red'>Format Invalid for Email Address!</span>", 'email')


            ######## password registration validation #######
    if len(request.form['password']) < 1:
        messages = True
        flash(f"<span style='color: red'>This field required!</span>", 'password')

    if len(request.form['confirmpassword']) < 1 or (request.form['confirmpassword'] != request.form['password']):
        messages = True
        flash(f"<span style='color: red'>Passwords do not match!</span>", 'confirmpassword')

              ######## email registration validation (if exists) #######
    emailQuery = "SELECT * FROM users WHERE email = %(email)s;"
    data = {"email" : request.form['email']}
    mysql = connectToMySQL("registration")
    results = mysql.query_db(emailQuery, data)
    if results:
        flash(f"<span style='color: red'>{request.form['email']} already exists. Try Again!</span>", 'email')
    elif messages == True:
        return redirect('/')
    else:
        addUserToDatabase(request.form['first_name'], request.form['last_name'], request.form['email'], request.form['password'])
        session['email'] = request.form['email']
        session['first_name'] = request.form['first_name']
        return redirect('/success') 

    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    if len(request.form['password']) < 1:
        flash(f"<span style='color: red'>*Field Required!</span>", 'log_password')
    mysql = connectToMySQL("registration")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {"email" : request.form['email']}
    result = mysql.query_db(query, data)
    if len(request.form['email']) < 1:
        flash(f"<span style='color: red'>This field required!</span>", 'log_email')
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['email'] = result[0]['email']
            session['first_name'] = result[0]['first_name']
            mysql = connectToMySQL("registration")
            query = "SELECT (user_level) FROM users WHERE email = %(email)s;"
            level = mysql.query_db(query, data)
            print(level)
            if level[0]['user_level'] == 9: # check to get admin access for user list
                return redirect('/admin')
            else:      
                return redirect('/success') # non-admin page
        else:
            flash(f"<span style='color: red'>Password Incorrect!</span>", 'log_password')
            return render_template('index.html')
    else:
        flash(f"<span style='color: red'>Email doesn't exist!</span>", 'log_email')

    return redirect('/')
    
def getUsers():
    mysql = connectToMySQL("registration")
    users = mysql.query_db("SELECT * FROM users")
    return users

@app.route('/admin')
def adminSuccess():
    if check_login():
        users = getUsers()
        return render_template('admin.html', users = users)
    else:
        return redirect('/')

def removeUser(id):
    mysql = connectToMySQL("registration")
    query = "DELETE FROM registration.users WHERE (`id` = %(id)s);"
    data = {"id": id}
    user = mysql.query_db(query, data)
    return user

@app.route("/remove/<id>")
def remove(id):
    removeUser(id)
    return redirect("/admin")

def removeAdmin(id):
    mysql = connectToMySQL("registration")
    query = "UPDATE users SET user_level = 1 WHERE (`id` = %(id)s);"
    data = {"id": id}
    regUser = mysql.query_db(query, data)
    return regUser

@app.route("/removeAdmin/<id>")
def byeAdmin(id):
    removeAdmin(id)
    return redirect("/admin")

def addAdmin(id):
    mysql = connectToMySQL("registration")
    query = "UPDATE users SET user_level = 9 WHERE (`id` = %(id)s);"
    data = {"id": id}
    newAdmin = mysql.query_db(query, data)
    return newAdmin

@app.route("/addAdmin/<id>")
def helloAdmin(id):
    addAdmin(id)
    return redirect("/admin")

@app.route('/success')
def success():
    if check_login():
        return render_template('success.html')
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)

