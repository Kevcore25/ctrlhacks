"""
Like 90% of comments are made by Kevin and Alvin
 
Kevin uses camelCase
Alvin uses snake_case
Jason uses camelCase sometimes snake_case
Jerry uses nocase (probably?)
"""

# Import Flask,  and its necessary "sublibraries"
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
# Import SHA256 for password encryption
from hashlib import sha256
import string
import random
import time
import json
# SQLITE
import sqlite3
sqlConnection = sqlite3.connect('snotes.db', check_same_thread=False)
dbcursor = sqlConnection.cursor()

#captcha deletion
import threading, time, os, sys

#captcha generator
from captcha.image import ImageCaptcha

# SHA256 salt
salt = "CTRL-HACKS"
# USERS

def verify_captcha(id, input):
    global captchas
    print("ASDUIHHUJIOASDIHUASDAUIOHSDASDHUIOOASDHUIOIHUASDIOAHUSDASDHUIO: " + str(captchas) + str(id))
    if input.lower() == captchas[id].lower():
        return True
    else:
        return False

def insert_user(
    username:   str,
    password:   str,
    email:      str,
    bio:        str,
    pfp_path:   str = 'pfp.png'
):
    """Creates a user, username MUST be unique to work. returns 0 when successfully inputted. -1 when username is already taken, and -2 for misc. error"""
    try:
        new_user = [(username, email, sha256(bytes(password+salt, 'utf-8')).hexdigest(), pfp_path, bio, str(int(time.time())))]
        
        print(f"Inserting: {new_user}")
        dbcursor.executemany(
                """
                INSERT INTO Users
                (
                    username,
                    email,
                    password,
                    pfp_path,
                    bio,
                    creation_date
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """, new_user
        )

        sqlConnection.commit()
        return 0
    except sqlite3.IntegrityError:
        return -1
    except:
        return -2

    
def user_data_get(
    username:   str
):
    """
    Returns the data of the user in the form of a tuple
    in the form (user_id, username, email, password, pfp_path, bio, creation_date)
    """
    result = dbcursor.execute(f"""
        SELECT * 
        FROM Users
        WHERE username = '{username}'
        LIMIT 1;
    """)

    return result.fetchone()

def delete_user(
    username:   str
):
    """Deletes a user with the username of username. if username doesn't exist, does nothing"""

    dbcursor.execute(f"""
        DELETE FROM Users
        WHERE username = '{username}';
        """)
    
    sqlConnection.commit()
    return 0

def user_edit_bio(
    new_bio:        str,
    username:       str
):
    dbcursor.execute(f"""
        UPDATE Users
        SET bio = '{new_bio}'
        WHERE username = '{username}';
    """)

    return 0

def all_user_get():
    """
    Returns the data of the user in the form of a tuple
    in the form (user_id, pfp_path, username, email, bio, creation_date (string, seconds))
    """
    result = dbcursor.execute(f"""
        SELECT * 
        FROM Users;
    """)

    return result.fetchall()
# NOTES
def insert_note(
    title:          str,
    description:    str,
    username:       str,
):
    """Inserts note data. Returns 1 when username is not a valid user. title MUST be unique or else returns -1"""
    try:
        user_id = user_data_get(username)

        if (user_id == None):
            return 1
        
        print(f"tuple1 = {user_id}")
        user_id = int(user_id[0])
        

        new_note = (user_id, str(int(time.time())), title, description)

        dbcursor.execute(f"""
            INSERT INTO Notes
            (
                user_id,
                note_date,
                title,
                description
            )
            VALUES
                (?, ?, ?, ?);
        """, new_note)

        sqlConnection.commit()
        return 0
    except sqlite3.IntegrityError:
        return -1
    except:
        return -2

def note_data_get(
    note_title: str
):
    """gets note data in the form (0: note_id, 1: note_date, 2: title, 3: description, 4: like_count, 5: dislike_count, 6: view_count, 7: user_id, 8: username, 9: pfp_path)"""
    dbcursor.execute(f"""
        SELECT *
        FROM vNote_data
        WHERE title = '{note_title}'
    """)
    return dbcursor.fetchone()

def delete_note(
    note_id:    int
):
    dbcursor.execute(f"""
        DELETE FROM Notes
        WHERE note_id = {note_id};
    """)
    sqlConnection.commit()
    return 0

def all_note_get():
    """Gets all note data"""

    result = dbcursor.execute("""
        SELECT *
        FROM vNote_data;
    """)
    return result.fetchall()

# CATEGORIES
def get_note_categories(
    note_id:    int
):
    dbcursor.execute(f"""
        SELECT *
        FROM vNote_categories
        WHERE note_id = {note_id};
    """)

    return 0

def all_categories():
    dbcursor.execute(f"""
        SELECT *
        FROM Categories;
    """)
    return dbcursor.fetchall()

def insert_category(
    category_name:  str,
    category_desc:  str
):
    """Creates a new category. returns 0 when complete, -1 when category name is already taken, and -2 for misc. error"""
    try:
        new_category = [(category_name, category_desc)]
        test = dbcursor.execute(f"""
            INSERT INTO Categories
            (
                category_name,
                category_desc
            )
            VALUES
                (?, ?);
        """, new_category)
        return 0
    except sqlite3.IntegrityError:
        return -1
    except:
        return -2

def set_note_category(
        category_name:  str,
        note_id:        int
    ):
    """sets a note to be in the category of the category name provided"""
    try:
        dbcursor.execute(f"""
            SELECT category_id
            FROM Categories
            WHERE category_name = '{category_name}';
        """)
        
        category_id = (dbcursor.fetchone())[0]
        if (category_id == None):
            return -1
        
        new_note_category = (note_id, category_id)
        print(new_note_category)
        dbcursor.execute(f"""
            INSERT INTO Note_Categories
            (
                note_id,
                category_id        
            )
            VALUES
                (?, ?);
        """, new_note_category) #execute takes a tuple, executemany takes a list of tuples
        sqlConnection.commit()
    except:
        return -2

def get_category_of_note(
        note_title:    int
    ):
    """DOES NOT WORK AS INTENDED: gets the categories a note has in the form of a list of tuples in the form of:
        (category_name (str), category_desc (str))"""
    note_id = note_data_get(note_title)
    dbcursor.execute(f"""
        SELECT category_name, category_desc
        FROM Categories
        LEFT JOIN Note_categories ON Categories.category_id = Note_categories.category_id
        WHERE note_id = {note_id};
    """)
    return dbcursor.fetchall()

def get_notes_in_category(
    category_name:  str
):
    """Returns a list of tuples in the form of:
        (note_id, note_date, title, description, like_count, dislike_count view_count, user_id, username, pfp_path)"""
    dbcursor.execute(f"""
        SELECT vNote_data.*
        FROM vNote_data
        INNER JOIN Note_categories ON Note_categories.note_id = vNote_data.note_id
        INNER JOIN Categories ON Categories.category_id = Note_categories.category_id
        WHERE category_name = '{category_name}';
    """)
    output = dbcursor.fetchall()
    if (output == None):
        return -1
    return dbcursor.fetchall()

def get_all_pto_pth():
    dbcursor.execute("SELECT * FROM Photos;")
    return dbcursor.fetchall()

def insert_new_photo(
    photo_path: str,
    note_title: str
):
    note_data = (user_data_get(note_title))
    
    if (note_data == None):
        return -1
    note_id = note_data[3]
    photo_data = (note_id, photo_path, int(str(time.time())))
    dbcursor.execute(f"""
        INSERT INTO Photos
        (
            note_id,
            photo_path,
            photo_date
        )
        VALUES
            (?,?,?)
    """, photo_data)
    


def verifySession(
    #username:   str,
    session:    str,
    detailed:   bool = False,
):
    """Checks if a session token is vaild or not"""

    with open('sessiontokens.json','r') as f:
        data = json.load(f)
    
    # if data[session]['username'] != username:
    #     return {"success": False, "reason": "unmatchingusernames", "reasonText": "Username does not match the Session token username!"} if detailed else False
    try:
        data[session]
    except KeyError:
        return {"success": False, "reason": "notfound", "reasonText": "Session token not found! It either has been expired, or removed!"} if detailed else False


    if time.time() > data[session]['expiresAt']:
        del data[session]

        with open('sessiontokens.json','w') as f:
            json.dump(data,f,indent=4)

        return {"success": False, "reason": "expired", "reasonText": "Session token expired!"} if detailed else False
    
    return {"success": True, "username": data[session]['username']} if detailed else True

    


# Assign app as the flask
app = Flask(__name__)

menu = [["Login", "/login.html"],["Register", "/register.html"],["Post Note", "/register.html"]]

# toolbar = f"""<input type="image" class="logo" src="https://cdn.discordapp.com/attachments/1150266843005722724/1154621939160195152/image.png" alt="SNOTES logo"  height="64" onclick="window.location.href='/'"><a class="headerlink" onclick="changeMode()" style="cursor:pointer;" id="changemode">Dark Mode</a>            <a class="headerlink" href="{ menu[0][1] }">{menu[0][0]}</a>           <a class="headerlink" href="{ menu[1][1] }">{ menu[1][0] }</a>       <a class="headerlink" href="{ menu[2][1] }"><span style="color: #FFAA00;">{ menu[2][0] }<span></a>"""
toolbar = ""
captchas = {}

def generate_captcha(token):
    global captchas
    print(f"captchas: {captchas}", file=sys.stdout)
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    captcha = ImageCaptcha(width=200, height=100)

    captcha.generate(captcha_text)
    captcha.write(captcha_text, f'templates/captchas/{token}.png')

    captchas[token] = captcha_text

    print(captcha, captcha_text)

    return captcha_text

note = {}

@app.route('/getnote', methods=["GET"])
def notes():
    return """<div class='note'>
            <h1>Title</h1>
            <div style="width: 25%;">
                <p>Description ofsdahkjusdahkjasdhjkasdhkjiasdhjkasdhkjadskhjasdhjkaskdjhasdhjkakshjd note</p>
            </div>
            <div style="font-size: small; color: rgb(88, 88, 88); text-align: right;">
                <p>Author: Jerry wu (123980123)</p>
            </div>
        </div>"""

@app.route('/result.html', methods=["GET"])
def welcome():
    global note
    with open("note.b64", "r") as f:
        note_image = f.read()
    return render_template(
      'result.html', 
      menu            = menu,

      image           = "static/logo.png", 
      title           = note['username'] + "'s " + note["title"],
      description     = note["description"],
      note_image      = note_image
    )

@app.route('/submit-note', methods=["POST"])
def submitNote():
    """
    Original Idea: Add a note to the SQLite database
    Current (out of time): Overwrites a global variable. Does not include a picture or others because of limited time
    """

    """
    Variables:

    sessionToken    - the session token submitted by the user. This confirms sessions as well as verifying that the token is vaild.
    title           - the title submitted by the user
    description     - the description submiited by the user
    """
    global note

    d = request.get_json(force=True) 
    try: 
        # Note. d.get is not necessary, as you can use d['sessionToken']
        sessionToken    = d.get('sessionToken')
        title           = d.get('title')
        description     = d.get('description')

    except KeyError:
        return Response(json.dumps({"success": False, "reason": "invaildarg", "reasonText": "Invaild arguments! Check your arguments and see if they are missing sessionToken, title, and description."}), mimetype='application/json')
    
    session = verifySession(sessionToken, detailed=True) # Provide a detailed view so the function can also get the username!

    if session['success']: # IF true
        # For now, instead of using SQL (Alvin hasn't coded it yet), we use a dict called note. This also means we need to global the var
        # Note overwrites the previous note. This is intended, but also not intended (Not our plan, we will fix it later)
        note = {
            "username": session['username'],
            "title": title,
            "description": description
        }
        return Response(json.dumps({"success": True}), mimetype='application/json')

    else:
        return Response(json.dumps({"success": False, "reason": session['reason'], "reasonText": session['reasonText']}), mimetype='application/json')




@app.route('/allusers')
def dbusers():
    return all_user_get()

@app.route('/allnotes')
def dbnotes():
    return all_note_get()

@app.route('/allcategories')
def dbcategories():
    return all_categories()

@app.route('/allphotos')
def dbphotos():
    return get_all_pto_pth()

@app.route('/dbtest')
def dbtest():
    a= insert_new_photo("hi/hi", "TEST")
    return int(a)

@app.route('/dbcommit')
def dbcommit():
    sqlConnection.commit()
    return "Done"

@app.route('/')
def indexPg():
    """Return"""
    return render_template('main.html', 
        menu = menu,
        toolbar = toolbar
    )

@app.route('/search')
def searching():
    return render_template('search.html', 
        menu = menu,
        toolbar = toolbar,
        image           = "static/logo.png", 
        title           = note['noteName'],
        description     = note["noteDescription"],
        subject     = note["subject"]
    )

@app.route('/post')
def posting():
    return render_template('post.html', 
        menu = menu,
        toolbar = toolbar
    )

def delete_captcha(captcha_id): 
    """
    Schedules a deletion of a captcha.
    Jerry's Bug fixed by Kevin reason: A schedule was made to delete the captcha after 5 seconds, giving the user no chance to type in the details to register an account. This was fixed to set a timer of 1 hr. Now, why does the picture affect the captcha dict? Who knows, I didn't make the captcha system 
    """
    global captchas
    time.sleep(3600)
    os.remove(f'templates/captchas/{captcha_id}.png')
    del captchas[captcha_id]

@app.route("/login.html")
def login():
    global captchas
    captcha_id = sha256(random.randbytes(8)).hexdigest()
    generate_captcha(captcha_id)

    #captcha deletion function (someone please make it delete on get)


    thread = threading.Thread(target=delete_captcha, args=[captcha_id])
    thread.start()

    return render_template(f"login.html", menu = menu, captcha_id=captcha_id, captcha_image=f'captchas/{captcha_id}.png')

    
@app.route("/submit-register", methods=["POST"])
def submit():
    """Registers an account based on the provided creditentals"""

    """
    Variables:

    username    - the username submitted by the user
    password    - the password submitted by the user
    email       - the email submitted by the user (ONLY for register)

    """

    try:
        username = request.form.get('username')
        password = request.form.get('password')
        email    = request.form.get('email')
        bio      = request.form.get('bio')
    except (KeyError, TypeError) as e: # Type error ?
        return Response(json.dumps({"success": False, "reason": str(e), "reasonText": "Invaild arguments most likely. Please check if you filled out all the arguments!"}), mimetype="application/json")
    
    pfp_path = None

    if verify_captcha(request.form.get("captcha_id"), request.form.get("captcha_input")):
        insert_user(username, password, email, bio, pfp_path)
        return Response(json.dumps({"success": True, "createdData": {"username": username, "password": password, "email": email}} ), mimetype="application/json")






@app.route("/submit-login", methods=["POST"])
def submitLogin():
    """The JS function part. It submits user data and returns a created session token to the user"""

    global captchas

    """
    Variables:

    username    - the username submitted by the user
    password    - the password submitted by the user
    """
    d = request.get_json(force=True) 
    username = d.get('username')
    password = d.get('password')

    data = user_data_get(username)

    # Expiry Time in seconds. After THIS amount of seconds, the token expires and the user will have to create another session token
    expiryTime = 60 * 60 # 1 hour

    # If the SHA256 of the password matches the hashed password in the DB, then create a session token
    if sha256(bytes(password + salt, 'utf-8')).hexdigest() == data[3]:
        if verify_captcha(d.get("captcha_id"), d.get("captcha_input")):

            # JSON is used because Kevin doesn't know how to use SQLite and time is ticking...
            # After the hackathon, this may be turned into a database because it is more secure and productive that way
            with open('sessiontokens.json', 'r') as f:
                data = json.load(f)
            
            tokenID = sha256( 
                bytes( 
                    username + str(time.time()) + str(random.randbytes(16)), # Essentially randomizes the token ID
                'utf-8')  
            ).hexdigest()

            data[tokenID] = {
                "username": username,
                "createdAt": time.time(),
                "expiresAt": time.time() + expiryTime
            }


            # This is used to redirect username to session token, instead of session token to username (slow)
            # Used to remove past session tokens, removing unnecessary sessions, reducing disk usage and resets the session
            # Again, this SHOULD be a database but Kevin doesn't know how to use it
            with open('usernamesessions.json', 'r') as f:
                us = json.load(f)

            try:
                us[username] # IF user exists, must mean a token was created before
                del data[us[username]] # Delete previous token since it's unnecessary anymore
            except: pass # Continue anyways

            us[username] = tokenID # Create it

            with open('usernamesessions.json', 'w') as f:
                json.dump(us, f, indent=4) # Indent 4 is not necessary. It just makes it easier to read

            # Dump the data
            with open('sessiontokens.json', 'w') as f:
                json.dump(data,f,indent=4)
            
            # Finally, return the response
            return Response(json.dumps({"success": True, "token": tokenID} | data[tokenID]), mimetype='application/json') # Creates a JSON string to use for the client
        else:
            return Response(json.dumps({"success": False, "reason": "invalidcaptcha", "reasonText": "The captcha is incorrect!"}), mimetype='application/json')
    else:
        return Response(json.dumps({"success": False, "reason": "invaildpassword", "reasonText": "The password is incorrect!"}), mimetype='application/json')



@app.route("/account/<username>")
def searchaccount(username):
    # (user_id, pfp_path, username, email, bio, creation_date (string, seconds))
    data = user_data_get(username)
    if data is None: return "<h1>Account is not found!</h1>"
    print(f"""\n\n\n\n\n\n\nDATA: {data}\n\n\n\n\n\n\n\n""")
    return render_template(
        f"accounttemp.html",
        username = str(username),
        userID = data[0],
        pfpPath = data[4],
        email = data[2],
        description = data[5],
        regDate = data[6],
        password = data[3],
        toolbar = toolbar,
        menu = menu
    )

@app.route("/register.html")
def register():
    global captchas
    captcha_id = sha256(random.randbytes(8)).hexdigest()
    generate_captcha(captcha_id)



    thread = threading.Thread(target=delete_captcha, args=[captcha_id])
    thread.start()
    
    return render_template(f"register.html", menu = menu, captcha_id=captcha_id, captcha_image=f'captchas/{captcha_id}.png')

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
         
    if request.method == 'GET':
        return render_template(f"profile.html", menu = menu, description = user_data_get(username)[5], username=username)
    else:
        user_edit_bio(request.form.get("description"), username)
        return render_template(f"profile.html", menu = menu, description = user_data_get(username)[5], username=username)
        
@app.route("/result", methods=["POST"])
def result(): 
    return render_template("result.html", c1="grade 10", c2="biology", description="very nice description")

@app.route('/<path:path>')
def servePath(path):

    """
    Serve the path. If the file from the path is not found, return the page of 404.html
    """
    
    # Assumes that no . are in path. Therefore, add a .html if for example, kcservers.ca/main
    if '.' not in path:
        path += '.html'


    try:
        if '.html' in path:
            return render_template(
                path, 
                menu = menu,
                toolbar = toolbar
            )
        else:
            return send_from_directory('templates', path)
    except (OSError, IOError):
        return render_template(
            '404.html',
            path = path                       
        )


# Main helps identity that the main process runs this command instead of other subprocesses
if __name__ == "__main__":
    app.run(debug=True, host="192.168.1.76", port=8000, use_reloader=False)

