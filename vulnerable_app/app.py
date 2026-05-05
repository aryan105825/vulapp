# vulnerable_app/app.py
from flask import Flask, request, render_template_string
import sqlite3, os, pickle, subprocess, requests

app = Flask(__name__)

# VULN 1: Hardcoded secret
SECRET_KEY = "hardcoded_super_secret_123"
DB_PASSWORD = "admin123"

# VULN 2: SQL Injection
@app.route("/user")
def get_user():
    user_id = request.args.get("id")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id  # direct concat
    cursor.execute(query)
    return str(cursor.fetchall())

# VULN 3: XSS
@app.route("/search")
def search():
    q = request.args.get("q", "")
    return render_template_string("<h1>Results for: " + q + "</h1>")  # unsanitized

# VULN 4: Command Injection
@app.route("/ping")
def ping():
    host = request.args.get("host")
    result = subprocess.check_output("ping -c 1 " + host, shell=True)  # shell=True + concat
    return result

# VULN 5: Path Traversal
@app.route("/file")
def read_file():
    filename = request.args.get("name")
    with open("/var/data/" + filename) as f:  # no sanitization
        return f.read()

# VULN 6: SSRF
@app.route("/fetch")
def fetch_url():
    url = request.args.get("url")
    return requests.get(url).text  # fetches any internal/external URL

# VULN 7: Insecure Deserialization
@app.route("/load", methods=["POST"])
def load_data():
    data = request.get_data()
    obj = pickle.loads(data)  # arbitrary code execution
    return str(obj)

# VULN 8: Missing Auth — admin panel exposed
@app.route("/admin/delete_user")
def delete_user():
    uid = request.args.get("uid")
    conn = sqlite3.connect("users.db")
    conn.execute("DELETE FROM users WHERE id = ?", (uid,))
    conn.commit()
    return "Deleted"

# VULN 9: IDOR
@app.route("/account/<user_id>")
def account(user_id):
    # No check that the requester owns this account
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return str(cursor.fetchone())

# VULN 10: eval() misuse
@app.route("/calc")
def calc():
    expr = request.args.get("expr")
    return str(eval(expr))  # RCE via eval

if __name__ == "__main__":
    app.run(debug=True)  # debug mode exposes stack traces + interactive console