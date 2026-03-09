from flask import Flask, request, redirect, render_template, jsonify
import sqlite3
import random
import string

app = Flask(__name__)


# ---------- DATABASE ----------

def get_db():
    return sqlite3.connect("links.db")


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS links (
            short TEXT PRIMARY KEY,
            original TEXT,
            clicks INTEGER
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------- UTILITY ----------

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))


# ---------- HOME ----------

@app.route("/")
def home():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT short, original, clicks FROM links")

    rows = c.fetchall()

    links = [
        {"short": r[0], "original": r[1], "clicks": r[2]}
        for r in rows
    ]

    conn.close()

    return render_template("index.html", links=links)


# ---------- SHORTEN URL ----------

@app.route("/shorten", methods=["POST"])
def shorten():

    url = request.form.get("url")

    if not url:
        return "Invalid URL"

    if not url.startswith("http"):
        url = "https://" + url

    code = generate_code()

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO links (short, original, clicks) VALUES (?, ?, ?)",
        (code, url, 0)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------- REDIRECT ----------

@app.route("/<code>")
def redirect_link(code):

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "SELECT original, clicks FROM links WHERE short=?",
        (code,)
    )

    row = c.fetchone()

    if row:

        original_url = row[0]
        clicks = row[1]

        c.execute(
            "UPDATE links SET clicks=? WHERE short=?",
            (clicks + 1, code)
        )

        conn.commit()
        conn.close()

        return redirect(original_url)

    conn.close()
    return "Not found"


# ---------- API FOR LIVE DASHBOARD ----------

@app.route("/api/links")
def get_links():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT short, original, clicks FROM links")

    rows = c.fetchall()

    links = [
        {"short": r[0], "original": r[1], "clicks": r[2]}
        for r in rows
    ]

    conn.close()

    return jsonify(links)


# ---------- RUN SERVER ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)