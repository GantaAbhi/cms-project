from flask import Flask, render_template, request
from datetime import datetime
import os

app = Flask(__name__)
CONTENT_DIR = "content"
HISTORY_FILE = os.path.join(CONTENT_DIR, "history.txt")
INDEX_FILE = os.path.join(CONTENT_DIR, "index.html")

# Ensure necessary files exist
os.makedirs(CONTENT_DIR, exist_ok=True)
open(INDEX_FILE, 'a').close()
open(HISTORY_FILE, 'a').close()

@app.route('/')
def public():
    with open(INDEX_FILE, "r", encoding='utf-8') as f:
        content = f.read()
    return render_template('index.html', content=content)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        content = request.form['content']

        # Save current content to history before updating
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "r", encoding='utf-8') as old_file:
                old_content = old_file.read()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_entry = f"--- Update at {timestamp} ---\n{old_content.strip()}\n\n"
            with open(HISTORY_FILE, "a", encoding='utf-8') as history:
                history.write(history_entry)

        # Save new content
        with open(INDEX_FILE, "w", encoding='utf-8') as f:
            f.write(content)

        return render_template('success.html')

    # Read last 5 updates from history.txt (from bottom)
    updates = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding='utf-8') as f:
            content = f.read().strip()
            chunks = content.split("--- Update at ")
            for chunk in chunks[::-1]:  # reverse for newest first
                if chunk.strip():
                    lines = chunk.strip().split("\n", 1)
                    timestamp = lines[0].strip()
                    text = lines[1].strip() if len(lines) > 1 else ""
                    updates.append((timestamp, text))
                if len(updates) == 5:
                    break

    # Read current content
    current_content = ""
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding='utf-8') as f:
            current_content = f.read()

    return render_template('admin.html', current=current_content, updates=updates)

@app.route('/success')
def success():
    return render_template('success.html')