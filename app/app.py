from flask import Flask, render_template, request
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
import time

app = Flask(__name__)

# Get DB connection details from environment variables
db_host = os.environ.get("DB_HOST", "localhost")
db_user = os.environ.get("DB_USER", "root")
db_password = os.environ.get("DB_PASSWORD", "root")
db_name = os.environ.get("DB_NAME", "cms")
# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    return connection

# Create table if not exists with retry logic
def init_db():
    for i in range(10):  # retry up to 10 times
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            print("✅ Database initialized.")
            break
        except Error as e:
            print(f"⏳ DB not ready, retrying in 3s... ({i+1}/10)")
            time.sleep(3)
    else:
        print("❌ Failed to connect to DB after 10 retries.")
        raise RuntimeError("DB initialization failed")

@app.route('/')
def public():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM content ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return render_template("index.html", content=result[0] if result else "No content availble")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        content = request.form['content']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO content (content) VALUES (%s)", (content,))
        conn.commit()
        conn.close()
        return render_template("success.html")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, content FROM content ORDER BY id DESC LIMIT 5")
    updates = cursor.fetchall()
    conn.close()
    return render_template("admin.html", updates=updates, current=updates[0][1] if updates else "")

@app.route('/success')
def success():
    return render_template("success.html")

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
