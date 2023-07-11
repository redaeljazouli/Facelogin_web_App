import os
import re
import io
import zlib
from werkzeug.utils import secure_filename
from flask import Response
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session ,url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import face_recognition
from PIL import Image
from base64 import b64encode, b64decode
import re
from datetime import datetime
import logging
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired



from helpers import apology, login_required
# Configure application
app = Flask(__name__)
#configure flask-socketio

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
#activaton du rechargement automatique des templates 
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter


# fonction qui s'exécute après chaque requête, définissant certaines en-têtes HTTP pour empêcher la mise en cache.
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Ceci initialise une base de données SQLite.
db = SQL("sqlite:///data.db")


@app.route("/")
@login_required
def home():


    return redirect("/home")
#Ceci définit une route pour la page d'accueil qui nécessite une connexion. Si l'utilisateur est connecté, il est redirigé vers "/home".
logging.basicConfig(filename='app.log', level=logging.INFO)
@app.route("/home")
@login_required
def index():
    #return render_template("index.html")
    current_time = datetime.now().strftime("%H:%M:%S") # Obtenir l'heure actuelle
    logging.info(f"Current time: {current_time}")  # log the current time

    print(current_time)
    return render_template("index.html", current_time=current_time)





#Ceci définit une autre route pour la page d'accueil qui nécessite une connexion. En affichant  également l'heure actuelle.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    #Définit une route pour la page de connexion.


    session.clear()

    #Efface toutes les données de session.
    if request.method == "POST":

        # Assign inputs to variables
        input_username = request.form.get("username")
        input_password = request.form.get("password")

        # Ensure username was submitted
        if not input_username:
            return render_template("login.html",messager = 1)



        # Ensure password was submitted
        elif not input_password:
             return render_template("login.html",messager = 2)

        # Query database for username
        username = db.execute("SELECT * FROM users WHERE username = :username",
                              username=input_username)

        # Ensure username exists and password is correct
        if len(username) != 1 or not check_password_hash(username[0]["hash"], input_password):
            return render_template("login.html",messager = 3)

        # Remember which user has logged in
        session["user_id"] = username[0]["id"]



        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Assign inputs to variables
        input_username = request.form.get("username")
        input_email = request.form.get("email")  # New line
        input_password = request.form.get("password")
        input_confirmation = request.form.get("confirmation")

        # Ensure username and email were submitted
        if not input_username:
            return render_template("register.html", message=1)

        elif not input_email:  # New condition
            return render_template("register.html", message="Vous devez fournir un email.")

        # Ensure password was submitted
        elif not input_password:
            return render_template("register.html", message=2)

        # Ensure password confirmation was submitted
        elif not input_confirmation:
            return render_template("register.html", message=4)
        
        #verification 

        elif  input_password != input_confirmation:
            return render_template("register.html", message=3)

        # Query database for username
        username = db.execute("SELECT username FROM users WHERE username = :username",
                              username=input_username)

        # Ensure username is not already taken
        if len(username) == 1:
            return render_template("register.html", message=5)

        # Query database to insert new user
        else:
            new_user = db.execute("INSERT INTO users (username, email, hash) VALUES (:username, :email, :password)",
                                  username=input_username,
                                  email=input_email,  # Include email in the INSERT
                                  password=generate_password_hash(input_password, method="pbkdf2:sha256", salt_length=8),)

            if new_user:
                # Keep newly registered user logged in
                session["user_id"] = new_user

            # Flash info for the user
            flash(f"Registered as {input_username}")

            # Redirect user to homepage
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/delete", methods=["GET"])
@login_required
def delete():
    users = db.execute("SELECT * FROM users")
    return render_template("delete.html", users=users)

@app.route("/delete/<username>", methods=["POST"])
@login_required
def delete_user(username):
    db.execute("DELETE FROM users WHERE username = :username", username=username)
    return redirect(url_for('delete'))

@app.route("/facereg", methods=["GET", "POST"])
def facereg():
    session.clear()
    if request.method == "POST":


        encoded_image = (request.form.get("pic")+"==").encode('utf-8')
        username = request.form.get("name")
        name = db.execute("SELECT * FROM users WHERE username = :username",
                        username=username)
              
        if len(name) != 1:
            return render_template("camera.html",message = 1)

        id_ = name[0]['id']    
        compressed_data = zlib.compress(encoded_image, 9) 
        
        uncompressed_data = zlib.decompress(compressed_data)
        
        decoded_data = b64decode(uncompressed_data)
        
        new_image_handle = open('./static/face/unknown/'+str(id_)+'.jpg', 'wb')
        
        new_image_handle.write(decoded_data)
        new_image_handle.close()
        try:
            image_of_bill = face_recognition.load_image_file(
            './static/face/'+str(id_)+'.jpg')
        except:
            return render_template("camera.html",message = 5)

        bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]

        unknown_image = face_recognition.load_image_file(
        './static/face/unknown/'+str(id_)+'.jpg')
        try:
            unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
        except:
            return render_template("camera.html",message = 2)


#  o    mpare faces
        results = face_recognition.compare_faces(
        [bill_face_encoding], unknown_face_encoding)

        if results[0]:
            username = db.execute("SELECT * FROM users WHERE username = :username",
                              username="swa")
            session["user_id"] = username[0]["id"]
            return redirect("/")
        else:
            return render_template("camera.html",message=3)


    else:
        return render_template("camera.html")

# Configurer Flask-Mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'redaeljazouli20@gmail.com'
app.config['MAIL_PASSWORD'] = 'okramctoiirumsok'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
#safekey 
app.secret_key = 'hadchimrdni'

# Configure Timed Serializer
s = URLSafeTimedSerializer(app.secret_key)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = db.execute("SELECT * FROM users WHERE email = :email", email=email)
        if len(user) != 1:
            flash('Adresse e-mail non reconnue.')
            return render_template('reset_password_request.html')
        else:
            token = s.dumps(email, salt='recover-key')
            msg = Message('Réinitialiser votre mot de passe', sender='noreply@demo.com', recipients=[email])
            link = url_for('reset_password', token=token, _external=True)
            msg.body = 'Cliquez sur le lien suivant pour réinitialiser votre mot de passe : {}'.format(link)
            mail.send(msg)
            flash('Veuillez vérifier votre e-mail pour les instructions de réinitialisation du mot de passe.')
            return redirect(url_for('login'))
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='recover-key', max_age=3600)
    except SignatureExpired:
        flash('Le lien de réinitialisation du mot de passe est invalide ou a expiré.')
        return redirect(url_for('reset_password_request'))
    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.')
            return render_template('reset_password.html', token=token)
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE users SET hash = :hashed_password WHERE email = :email", hashed_password=hashed_password, email=email)
        flash('Votre mot de passe a été mis à jour.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)


@app.route("/facesetup", methods=["GET", "POST"])
def facesetup():
    if request.method == "POST":


        encoded_image = (request.form.get("pic")+"==").encode('utf-8')


        id_=db.execute("SELECT id FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["id"]
        # id_ = db.execute("SELECT id FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["id"]    
        compressed_data = zlib.compress(encoded_image, 9) 
        
        uncompressed_data = zlib.decompress(compressed_data)
        decoded_data = b64decode(uncompressed_data)
        
        new_image_handle = open('./static/face/'+str(id_)+'.jpg', 'wb')
        
        new_image_handle.write(decoded_data)
        new_image_handle.close()
        image_of_bill = face_recognition.load_image_file(
        './static/face/'+str(id_)+'.jpg')    
        try:
            bill_face_encoding = face_recognition.face_encodings(image_of_bill)[0]
        except:    
            return render_template("face.html",message = 1)
        return redirect("/home")

    else:
        return render_template("face.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html",e = e)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
      app.run()
