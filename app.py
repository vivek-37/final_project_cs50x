import os

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///medilog.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET","POST"])
@login_required
def home():
    """TODO: Make a Homepage where users can view their added family members and their ongoing medical problems.
            Homepage has a big logo of Medilog in a grid as the top left element, top right element is a nested grid displaying
            upto 4 family member illnesses/injuries (if any). Bottom will display number of ongoing illnesses/injuries in the family and
            2 other relevant sentences.
            UI is reminiscent of google classrooms or google groups
            Menu Sidebar should be available everywhere
    """
    # Handle case where register form filled but exit at first member via redirect to first member form
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])
    if (len(family) < 1):
        return redirect("/firstMember")

    healthy = db.execute("SELECT * FROM families WHERE user_id = ? AND health_status = ?", session["user_id"], 0)
    illORinjured = db.execute("SELECT * FROM families WHERE user_id = ? AND health_status = ?", session["user_id"], 1)
    critical = db.execute("SELECT * FROM families WHERE user_id = ? AND health_status = ?", session["user_id"], 2)

    # Display upto 4 cards of family members as quick access, first red, then yellow, then green
    patients = len(critical) + len(illORinjured)

    if len(critical) >= min(4,len(family)):                         # 4 or more Red
        cards = [critical[i] for i in range(min(4,len(family)))]

    elif len(illORinjured) >= (min(4,len(family)) - len(critical)):     # 4 or more Red + Yellow
        Ccards = [critical[i] for i in range(len(critical))]
        Icards = [illORinjured[i] for i in range(min(4,len(family))-len(critical))]
        cards = Ccards + Icards

    else:                                                               # Red + Yellow less than 4
        Ccards = [critical[i] for i in range(len(critical))]
        Icards = [illORinjured[i] for i in range(len(illORinjured))]
        Hcards = [healthy[i] for i in range(min(4,len(family))-len(illORinjured)-len(critical))]
        cards = Ccards + Icards + Hcards


    # Fill the card content with most recent log title
    logs = db.execute("SELECT * FROM logs WHERE user_id = ? ORDER BY date_added DESC", session["user_id"])
    for card in cards:
        card.update({'recent' : 'No logs added yet'})
        for log in logs:
            if card['member_id'] == log['member_id']:
                card.update({'recent' : log['title']})

    # User enters the main homepage
    return render_template("home.html",family=family, cards=cards, patients=patients)

@app.route("/delete/<int:user_id>", methods=["GET"])
@login_required
def delete(user_id):
    """Delete account"""
    # Validate user
    correct_user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    if session["user_id"] != correct_user[0]["id"]:
        return apology("permissison denied",403)

    # Delete all user logs and all user family members
    db.execute("DELETE FROM logs WHERE user_id = ?", user_id)
    db.execute("DELETE FROM families WHERE user_id = ?", user_id)
    db.execute("DELETE FROM users WHERE id = ?", user_id)
    return redirect("/register")

@app.route("/addMember", methods=["GET","POST"])
@login_required
def addMember():
    """Form asking for basic information of new member in the user's family"""

    # Handle case where register form filled but exit at first member via redirect to first member form
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])
    if (len(family) < 1):
        return redirect("/firstMember")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("name"):
            return apology("must provide name", 400)
        elif not request.form.get("dob"):
            return apology("must provide dob", 400)
        elif not request.form.get("gender"):
            return apology("must provide gender", 400)
        elif not request.form.get("color"):
            return apology("must provide color", 400)
        else:
            name = request.form.get("name")
            dob = request.form.get("dob")
            gender = request.form.get("gender")
            color = request.form.get("color")

            # check for already existing members
            dupes = db.execute("SELECT * FROM families WHERE user_id = ? AND member_name = ? AND member_dob = ? AND member_gender = ? AND color = ?",session["user_id"], name, dob, gender, color)
            if dupes != []:
                return apology("member already exists", 403)

            # enter the new member into the family
            db.execute("INSERT INTO families (user_id,member_name,member_dob,member_gender,color) VALUES(?,?,?,?,?)", session["user_id"],name,dob,gender,color)

            # enter the user into the homepage after adding
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("addMember.html", family=family)

@app.route("/deleteMember/<int:member_id>", methods=["GET","POST"])
@login_required
def deleteMember(member_id):
    """Delete family member"""
    # Validate user
    correct_owner = db.execute("SELECT * FROM families WHERE member_id = ?", member_id)
    if session["user_id"] != correct_owner[0]["user_id"]:
        return apology("permissison denied", 403)

    # Delete all member logs then delete member
    db.execute("DELETE FROM logs WHERE member_id = ?", member_id)
    db.execute("DELETE FROM families WHERE member_id = ?", member_id)
    return redirect("/settings")

@app.route("/editMember/<int:member_id>", methods=["GET","POST"])
@login_required
def editMemberForm(member_id):
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])
    member = db.execute("SELECT * FROM families WHERE member_id = ?", member_id)
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("name"):
            return apology("must provide name", 400)
        elif not request.form.get("dob"):
            return apology("must provide dob", 400)
        elif not request.form.get("gender"):
            return apology("must provide gender", 400)
        elif not request.form.get("color"):
            return apology("must provide color", 400)
        else:
            name = request.form.get("name")
            dob = request.form.get("dob")
            gender = request.form.get("gender")
            color = request.form.get("color")

            # Check for already existing members
            dupes = db.execute("SELECT * FROM families WHERE user_id = ? AND member_name = ? AND member_dob = ? AND member_gender = ? AND color = ?",session["user_id"], name, dob, gender, color)
            if len(dupes) != 0:
                return apology("member already exists", 403)

            # Update member
            db.execute("UPDATE families SET (member_name) = ?, (member_dob) = ?, (member_gender) = ?, (color) = ? WHERE member_id = ?",name,dob,gender,color, member_id)

            # enter the user into the homepage after updating
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("editMember.html", family=family, member=member[0])

@app.route("/firstMember", methods=["GET", "POST"])
def firstMemberForm():
    """Form asking for basic information of first member in the user's family right after registering"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("name"):
            return apology("must provide name", 400)
        elif not request.form.get("dob"):
            return apology("must provide dob", 400)
        elif not request.form.get("gender"):
            return apology("must provide gender", 400)
        elif not request.form.get("color"):
            return apology("must provide color", 400)
        else:
            # Try to get first member and handle the case where user re enters first meber form after already entering
            try:
                name = request.form.get("name")
                dob = request.form.get("dob")
                gender = request.form.get("gender")
                color = request.form.get("color")

                db.execute("INSERT INTO families (user_id,member_name,member_dob,member_gender,color) VALUES(?,?,?,?,?)", session["user_id"],name,dob,gender,color)

                # Enter the user into the website after registering
                return redirect("/")

            except ValueError:
                return apology("first member already exists", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("firstMember.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user into the website """

    # Forget any previous session
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query the database for usernames
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # let the user into the website
        session["user_id"] = rows[0]["id"]
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

@app.route("/logs", methods=["GET", "POST"])
@login_required
def logs():
    """TODO:Users can add new Medical logs and access older medical logs in an email type UI.
            A Medical log in this webpage is defined as a short decription of a user defined medical report/log with a link to a webpage for in-detail descriptions.
            Users can search logs normally or also by using filters like Date added, Family Member, Disease/Injury type: Ongoing/Recovered, etc.
    """
    # Load family members into sidebar
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])

    # Load logs to be displayed
    logs = db.execute("SELECT * FROM logs WHERE user_id = ?",session["user_id"])
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("search"):
            return render_template("logs.html", family=family, logs=logs)

        # load logs with search query in the title
        search_logs = db.execute("SELECT * FROM logs WHERE user_id = ? AND title LIKE ?", session["user_id"], "%" + request.form.get("search") + "%")
        for i in range(len(logs)):
            if logs[i] not in search_logs:
                search_logs.append(logs[i])
        return render_template("logs.html", family=family,  logs=search_logs)

    else:
        # User reached route via GET
        return render_template("logs.html", family=family, logs=logs)

@app.route("/logs/create", methods=["GET","POST"])
@login_required
def logCreate():

    # Load family members into sidebar
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("title"):
            return apology("must provide title", 400)
        elif not request.form.get("patient"):
            return apology("must select the patient", 400)
        elif not request.form.get("dofsi"):
            return apology("must provide the dofsi", 400)
        elif not request.form.get("issue"):
            return apology("must specify type of issue", 400)
        elif not request.form.get("cond"):
            return apology("must specify condition", 400)
        elif not request.form.get("dia"):
            return apology("must confirm diagnosis", 400)
        if (request.form.get("dia") == 'y'):
            if not request.form.get("hosp"):
                return apology("must provide hospital details", 400)
            elif not request.form.get("doct"):
                return apology("must provide doctors' details", 400)
            elif not request.form.get("diares"):
                return apology("must provide result of diagnosis", 400)
            elif not request.form.get("recadv"):
                return apology("must provide recovery advice", 400)
            elif not request.form.get("med"):
                return apology("must provide prescription", 400)

            # If member_id is changed on client side, throw error
            flag = 0
            for member in family:
                if request.form.get("patient") == str(member["member_id"]):
                    flag = 1
            if not flag:
                return apology("invalid member", 403)

            #   If plan to add bg color for option    member = db.execute("SELECT * FROM families WHERE member_id = ?", request.form.get("patient"))

            # Enter the values into the table
            db.execute(
                "INSERT INTO logs (user_id,member_id,title,date_added,dofsi,health_issue,condition,diagnosed,hospital_info,doctors,diagnosis_result,recovery_advice,prescription) VALUES(?,?,?,datetime('now'),?,?,?,?,?,?,?,?,?)",
                session["user_id"],request.form.get("patient"),request.form.get("title"),request.form.get("dofsi"),request.form.get("issue"),request.form.get("cond"),request.form.get("dia"),
                request.form.get("hosp"),request.form.get("doct"),request.form.get("diares"),request.form.get("recadv"),request.form.get("med")
            )
        else:

            # If member_id is changed on client side, throw error
            flag = 0
            for member in family:
                if request.form.get("patient") == str(member["member_id"]):
                    flag = 1
            if not flag:
                return apology("invalid member", 403)

            # Enter the values into the table
            db.execute(
                "INSERT INTO logs (user_id,member_id,title,date_added,dofsi,health_issue,condition,diagnosed) VALUES(?,?,?,datetime('now'),?,?,?,?)",
                session["user_id"],request.form.get("patient"),request.form.get("title"),request.form.get("dofsi"),request.form.get("issue"),request.form.get("cond"),request.form.get("dia"),
            )

        # Update family member health
        if request.form.get("issue") == 'o':
            if request.form.get("cond") == 'c':
                db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 2, request.form.get("patient"))
            else:
                db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 1, request.form.get("patient"))
        else:
            db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 0, request.form.get("patient"))

        # Redirect user back to the logs page
        return redirect("/logs")
    else:
        # User reached route via GET
        return render_template("createLog.html", family=family)

@app.route("/logs/delete/<int:log_id>", methods=["GET","POST"])
@login_required
def logDelete(log_id):
    """TODO:
    """
    # Add if condition; if user types different log_id in link directly
    log_owner = db.execute("SELECT * FROM logs WHERE log_id = ?", log_id)
    if session["user_id"] != log_owner[0]["user_id"]:
        return apology("permission denied", 403)

    # Delete log, update member health status and redirect to logs
    member_logs = db.execute("SELECT * FROM logs WHERE member_id = ?", log_owner[0]["member_id"])
    flag = 0
    for ml in member_logs:
        if ml["health_issue"] == 'o' and ml["condition"] == 'c' and ml["log_id"] != log_id:
            db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 2, log_owner[0]["member_id"])
            flag = 1
            break
    if flag == 0:
        for ml in member_logs:
            if ml["health_issue"] == 'o' and ml["condition"] == 's' and ml["log_id"] != log_id:
                db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 1, log_owner[0]["member_id"])
                flag = 1
                break
    if flag == 0:
        db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 0, log_owner[0]["member_id"])
    db.execute("DELETE FROM logs WHERE user_id = ? AND log_id = ?", session["user_id"], log_id)
    return redirect("/logs")

@app.route("/logs/edit/<int:log_id>", methods=["GET","POST"])
@login_required
def logEdit(log_id):
    """TODO:
    """
    # Add if condition; if user types different log_id in link directly
    log_owner = db.execute("SELECT * FROM logs WHERE log_id = ?", log_id)
    if session["user_id"] != log_owner[0]["user_id"]:
        return apology("permission denied", 403)

    # Load family members into sidebar
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("title"):
            return apology("must provide title", 400)
        elif not request.form.get("patient"):
            return apology("must select the patient", 400)
        elif not request.form.get("dofsi"):
            return apology("must provide the dofsi", 400)
        elif not request.form.get("issue"):
            return apology("must specify type of issue", 400)
        elif not request.form.get("cond"):
            return apology("must specify condition", 400)
        elif not request.form.get("dia"):
            return apology("must confirm diagnosis", 400)
        if (request.form.get("dia") == 'y'):
            if not request.form.get("hosp"):
                return apology("must provide hospital details", 400)
            elif not request.form.get("doct"):
                return apology("must provide doctors' details", 400)
            elif not request.form.get("diares"):
                return apology("must provide result of diagnosis", 400)
            elif not request.form.get("recadv"):
                return apology("must provide recovery advice", 400)
            elif not request.form.get("med"):
                return apology("must provide prescription", 400)

            # If member_id is changed on client side, throw error
            flag = 0
            for member in family:
                if request.form.get("patient") == str(member["member_id"]):
                    flag = 1
            if not flag:
                return apology("invalid member", 403)

            #   If plan to add bg color for option    member = db.execute("SELECT * FROM families WHERE member_id = ?", request.form.get("patient"))

            # Enter the values into the table
            db.execute(
                "UPDATE logs SET (member_id) = ?, (title) = ?,(dofsi) = ?,(health_issue) = ?,(condition) = ?,(diagnosed) = ?,(hospital_info) = ?,(doctors) = ?,(diagnosis_result) = ?,(recovery_advice) = ?,(prescription) = ? WHERE log_id = ?",
                request.form.get("patient"),request.form.get("title"),request.form.get("dofsi"),request.form.get("issue"),request.form.get("cond"),request.form.get("dia"),
                request.form.get("hosp"),request.form.get("doct"),request.form.get("diares"),request.form.get("recadv"),request.form.get("med"),log_id
            )
        else:

            # If member_id is changed on client side, throw error
            flag = 0
            for member in family:
                if request.form.get("patient") == str(member["member_id"]):
                    flag = 1
            if not flag:
                return apology("invalid member", 403)

            # Enter the values into the table
            db.execute(
                "UPDATE logs SET (member_id) = ?, (title) = ?,(dofsi) = ?,(health_issue) = ?,(condition) = ?,(diagnosed) = ? WHERE log_id = ?",
                request.form.get("patient"),request.form.get("title"),request.form.get("dofsi"),request.form.get("issue"),request.form.get("cond"),request.form.get("dia"),log_id
            )

        # Update family member health
        if request.form.get("issue") == 'o':
            if request.form.get("cond") == 'c':
                db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 2, request.form.get("patient"))
            else:
                db.execute("UPDATE families SET (health_status) = ? WHERE member_id = ?", 1, request.form.get("patient"))

        # Redirect user back to the logs page
        return redirect("/logs")
    else:
        # User reached route via GET
        return render_template("editLog.html", family=family, log=log_owner[0])

@app.route("/logs/view/<int:log_id>", methods=["GET","POST"])
@login_required
def logView(log_id):
    """TODO:
    """
    # Add if condition; if user types different log_id in link directly
    log_owner = db.execute("SELECT * FROM logs WHERE log_id = ?", log_id)
    if session["user_id"] != log_owner[0]["user_id"]:
        return apology("permission denied", 403)

    # Load family members into sidebar
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        return redirect(f"/logs/edit/{log_id}")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("viewLog.html", family=family, log=log_owner[0])


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Log user into the website """

    # Forget any previous session
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirm"):
            return apology("must provide password", 403)
        else:
            #try to get unique username
            try:
                name = request.form.get("username")
                password = request.form.get("password")
                confirm = request.form.get("confirm")

                if confirm != password:
                    return apology("confirm password correctly", 400)

                hashed = generate_password_hash(password)
                db.execute("INSERT INTO users (username, hash) VALUES(?,?)", name, hashed)

                # enter the user into the first member form after registering
                rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
                session["user_id"] = rows[0]["id"]
                return redirect("/firstMember")

            except ValueError:
                return apology("username already exists", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    # Load username directly if redirected from settings
    user = None
    if "user_id" in session.keys():
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Check for any missing inputs
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirm"):
            return apology("must provide password", 403)

        else:
            # try to get an existing username, if found, update the password
            try:
                name = request.form.get("username")
                password = request.form.get("password")
                confirm = request.form.get("confirm")

                if confirm != password:
                    return apology("confirm password correctly", 400)

                if user:
                    if name != user[0]["username"]:
                        return apology("permission denied", 403)

                auth = db.execute("SELECT * FROM users WHERE username = ?", name)

                if len(auth) == 0:
                    return apology("invalid username", 400)

                hashed = generate_password_hash(password)
                db.execute("UPDATE users SET hash = ? WHERE username = ?", hashed, name)

                # enter the user into the first member form after registering
                session["user_id"] = auth[0]["id"]
                return redirect("/")

            except ValueError:
                return apology("username already exists", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("resetPassword.html")


@app.route("/settings", methods=["GET"])
@login_required
def settings():
    """ Allow user to view username, family member list, remove family members, view stats of account """

    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])
    healthy = db.execute("SELECT * FROM families WHERE user_id = ? AND health_status = ?", session["user_id"], 0)
    illORinjured = db.execute("SELECT * FROM families WHERE user_id = ? AND health_status = ?", session["user_id"], 1)
    critical = db.execute("SELECT * FROM families WHERE user_id = ? AND health_status = ?", session["user_id"], 2)
    user_logs = db.execute("SELECT * FROM logs WHERE user_id = ?", session["user_id"])
    return render_template("settings.html", family=family, user=user[0],
                            fam_size=len(family), no_of_logs=len(user_logs),healthy=len(healthy), patients=len(illORinjured)+len(critical))
