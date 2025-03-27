import csv
import datetime
import requests
import urllib
import uuid

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///medilog.db")

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        # Handle case where register form filled but exit at first member via redirect to first member form
        family = db.execute("SELECT * FROM families WHERE user_id = ?", session["user_id"])
        if (len(family) < 1):
            return redirect("/firstMember")
        return f(*args, **kwargs)

    return decorated_function
