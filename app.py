from flask import Flask, request, jsonify
import requests
import sqlite3
import time
import random
import string

app = Flask(__name__)

# 👉 external data source (you can change later)
BASE_URL = "https://yash-code-with-ai.alphamovies.workers.dev/"

# ------------------ DATABASE ------------------
def init_db():
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            key TEXT PRIMARY KEY,
            expiry REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------ KEY SYSTEM ------------------
def generate_key(duration):
    key = "VERNEX-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    if duration == "lifetime":
        expiry = 9999999999
    else:
        expiry = time.time() + duration

    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys VALUES (?, ?)", (key, expiry))
    conn.commit()
    conn.close()

    return key, expiry

def is_valid(key):
    conn = sqlite3.connect("keys.db")
    c = conn.cursor()
    c.execute("SELECT expiry FROM keys WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()

    if not row:
        return False

    return time.time() < row[0]

# ------------------ PLANS ------------------
DURATIONS = {
    "1d": 86400,
    "2d": 172800,
    "3d": 259200,
    "7d": 604800,
    "30d": 2592000,
    "60d": 5184000,
    "lifetime": "lifetime"
}

# ------------------ ROUTES ------------------
@app.route("/")
def home():
    return "Vernex API + Key System LIVE 🚀"

@app.route("/generate")
def generate():
    plan = request.args.get("plan", "1d")

    if plan not in DURATIONS:
        return jsonify({"error": "Invalid plan"})

    key, expiry = generate_key(DURATIONS[plan])

    return jsonify({
        "key": key,
        "plan": plan,
        "expires_at": expiry
    })

@app.route("/api/numinfo")
def numinfo():
    num = request.args.get("num")
    key = request.args.get("key")

    if not is_valid(key):
        return jsonify({"error": "Invalid or expired key"})

    try:
        res = requests.get(BASE_URL, params={
            "num": num,
            "key": "7189814021"
        }, timeout=10)

        return jsonify(res.json())

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run()
