# from flask import Flask, request, redirect, render_template, jsonify, session
# import sqlite3
# import random
# import string

# app = Flask(__name__)
# app.secret_key = "vibeathon_secret"


# def get_db():
#     return sqlite3.connect("links.db")
# app = Flask(__name__)


# # ---------- DATABASE ----------

# def get_db():
#     return sqlite3.connect("links.db")


# def init_db():
#     conn = get_db()
#     c = conn.cursor()

#     c.execute("""
#         CREATE TABLE IF NOT EXISTS links (
#             short TEXT PRIMARY KEY,
#             original TEXT,
#             clicks INTEGER
#         )
#     """)

#     conn.commit()
#     conn.close()


# init_db()


# # ---------- UTILITY ----------

# def generate_code():
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=5))


# # ---------- HOME ----------

# @app.route("/")
# def home():

#     conn = get_db()
#     c = conn.cursor()

#     c.execute("SELECT short, original, clicks, max_clicks, active, created_at, last_accessed FROM links")

#     rows = c.fetchall()

#     links = [
#         {
#             "short": r[0],
#             "original": r[1],
#             "clicks": r[2],
#             "max_clicks": r[3],
#             "active": r[4],
#             "created_at": r[5],
#             "last_accessed": r[6]
#         }
#         for r in rows
#     ]

#     conn.close()

#     return render_template("index.html", links=links)

# # ---------- SHORTEN URL ----------

# @app.route("/shorten", methods=["POST"])
# def shorten():

#     url = request.form.get("url")
#     max_clicks = request.form.get("max_clicks")

#     if not url:
#         return "Invalid URL"

#     if not url.startswith("http"):
#         url = "https://" + url

#     code = generate_code()

#     import datetime
#     created_at = datetime.datetime.now()

#     conn = get_db()
#     c = conn.cursor()

#     c.execute(
#         """INSERT INTO links
#         (short, original, clicks, max_clicks, active, created_at, last_accessed)
#         VALUES (?, ?, ?, ?, ?, ?, ?)""",
#         (code, url, 0, max_clicks, 1, created_at, None)
#     )

#     conn.commit()
#     conn.close()

#     return redirect("/")
# @app.route("/edit/<code>", methods=["POST"])
# def edit(code):

#     new_url = request.form.get("new_url")

#     if not new_url.startswith("http"):
#         new_url = "https://" + new_url

#     conn = get_db()
#     c = conn.cursor()

#     c.execute("UPDATE links SET original=? WHERE short=?", (new_url, code))

#     conn.commit()
#     conn.close()

#     return redirect("/")
# # ---------- REDIRECT ----------

# @app.route("/<code>")
# def redirect_link(code):

#     conn = get_db()
#     c = conn.cursor()

#     c.execute("SELECT original, clicks, max_clicks, active FROM links WHERE short=?", (code,))
#     row = c.fetchone()

#     if not row:
#         return "Link not found"

#     original, clicks, max_clicks, active = row

#     if active == 0:
#         return "Link is disabled"

#     if max_clicks and clicks >= max_clicks:
#         return "Link expired"

#     import datetime
#     last_access = datetime.datetime.now()

#     c.execute(
#         "UPDATE links SET clicks=?, last_accessed=? WHERE short=?",
#         (clicks + 1, last_access, code)
#     )

#     conn.commit()
#     conn.close()

#     return redirect(original)

# @app.route("/toggle/<code>")
# def toggle(code):

#     conn = get_db()
#     c = conn.cursor()

#     c.execute("SELECT active FROM links WHERE short=?", (code,))
#     active = c.fetchone()[0]

#     new_status = 0 if active == 1 else 1

#     c.execute("UPDATE links SET active=? WHERE short=?", (new_status, code))

#     conn.commit()
#     conn.close()

#     return redirect("/")
# # ---------- API FOR LIVE DASHBOARD ----------

# @app.route("/api/links")
# def get_links():

#     conn = get_db()
#     c = conn.cursor()

#     c.execute("SELECT short, original, clicks FROM links")

#     rows = c.fetchall()

#     links = [
#         {"short": r[0], "original": r[1], "clicks": r[2]}
#         for r in rows
#     ]

#     conn.close()

#     return jsonify(links)
# import sqlite3

# conn = sqlite3.connect("links.db")
# cursor = conn.cursor()

# cursor.execute("PRAGMA table_info(links)")
# columns = cursor.fetchall()

# for col in columns:
#     print(col)

# conn.close()

# # ---------- RUN SERVER ----------

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=10000)

from flask import Flask, request, redirect, render_template, jsonify, session
import sqlite3
import random
import string
import datetime

app = Flask(__name__)
app.secret_key = "vibeathon_secret"


# ---------- DATABASE ----------

def get_db():
    return sqlite3.connect("links.db")


def init_db():
    conn = get_db()
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # LINKS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS links(
        short TEXT PRIMARY KEY,
        original TEXT,
        clicks INTEGER DEFAULT 0,
        max_clicks INTEGER,
        active INTEGER DEFAULT 1,
        created_at TEXT,
        last_accessed TEXT,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
init_db()

# ---------- UTIL ----------

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))


# ---------- REGISTER ----------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users(username,password) VALUES (?,?)",
                (username,password)
            )
            conn.commit()
        except:
            return "Username already exists"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------- LOGIN ----------

@app.route("/login", methods=["GET","POST"])
def login():

    if "user_id" in session:
        return redirect("/")

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/")

        return "Invalid login"

    return render_template("login.html")


# ---------- LOGOUT ----------

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")


# ---------- DASHBOARD ----------

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT short, original, clicks, max_clicks,
        active, created_at, last_accessed
        FROM links
        WHERE user_id=?
    """,(session["user_id"],))

    rows = c.fetchall()

    links = [
        {
            "short":r[0],
            "original":r[1],
            "clicks":r[2],
            "max_clicks":r[3],
            "active":r[4],
            "created_at":r[5],
            "last_accessed":r[6]
        }
        for r in rows
    ]

    conn.close()

    return render_template("index.html",links=links)


# ---------- CREATE SHORT LINK ----------

@app.route("/shorten",methods=["POST"])
def shorten():

    if "user_id" not in session:
        return redirect("/login")

    url = request.form.get("url")
    max_clicks = request.form.get("max_clicks")

    if not url:
        return "Invalid URL"

    if not url.startswith("http"):
        url = "https://" + url

    code = generate_code()
    created_at = datetime.datetime.now()

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        INSERT INTO links
        (short, original, clicks, max_clicks,
        active, created_at, last_accessed, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (code,url,0,max_clicks,1,created_at,None,session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/")


# ---------- EDIT DESTINATION ----------

@app.route("/edit/<code>",methods=["POST"])
def edit(code):

    new_url = request.form.get("new_url")

    if not new_url.startswith("http"):
        new_url = "https://" + new_url

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "UPDATE links SET original=? WHERE short=?",
        (new_url,code)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------- ENABLE / DISABLE ----------

@app.route("/toggle/<code>")
def toggle(code):

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT active FROM links WHERE short=?", (code,))
    active = c.fetchone()[0]

    new_status = 0 if active == 1 else 1

    c.execute(
        "UPDATE links SET active=? WHERE short=?",
        (new_status,code)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------- REDIRECT ----------

@app.route("/<code>")
def redirect_link(code):

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT original, clicks, max_clicks, active
        FROM links
        WHERE short=?
    """,(code,))

    row = c.fetchone()

    if not row:
        return "Link not found"

    original,clicks,max_clicks,active = row

    if active == 0:
        return "Link is disabled"

    if max_clicks and clicks >= max_clicks:
        return "Link expired"

    last_access = datetime.datetime.now()

    c.execute(
        "UPDATE links SET clicks=?, last_accessed=? WHERE short=?",
        (clicks+1,last_access,code)
    )

    conn.commit()
    conn.close()

    return redirect(original)
import sqlite3

@app.route("/api/links")
def get_links():
    if "user_id" not in session:
        return jsonify([])

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT short, original, clicks FROM links WHERE user_id=?", (session["user_id"],))
    rows = c.fetchall()

    links = [{"short": r[0], "original": r[1], "clicks": r[2]} for r in rows]
    conn.close()

    return jsonify(links)
# ---------- RUN ----------

if __name__ == "__main__":
    import webbrowser
    import threading
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:10000/login")).start()
    app.run(host="0.0.0.0", port=10000)