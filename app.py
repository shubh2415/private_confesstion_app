from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
from urllib.parse import urlparse

app = Flask(__name__)

# Environment variable se secret key lein, agar na mile toh default istemal karein
# Render par SECRET_KEY set karna zaroori hai
app.secret_key = os.environ.get('SECRET_KEY', 'ek-bahut-hi-strong-default-key-local')

def get_db_connection():
    """Database se connection banata hai."""
    # Render par set kiye gaye DATABASE_URI environment variable ko padhein
    db_uri = os.environ.get('DATABASE_URI')

    if not db_uri:
        # Agar URI set nahi hai toh error de
        raise ValueError("DATABASE_URI environment variable set nahi hai")

    # URI ko parse karke uske hisson ko alag karein
    # Format: mysql://user:password@host:port/database
    result = urlparse(db_uri)
    
    # Connection banayein
    return mysql.connector.connect(
        host=result.hostname,
        user=result.username,
        password=result.password,
        port=result.port,
        database=result.path[1:]  # path se shuru ka '/' hatane ke liye
    )

@app.route('/')
def login():
    return render_template('login.html', error=None)

@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        return redirect(url_for('welcome'))
    else:
        return render_template('login.html', error="Invalid credentials")

@app.route('/signup')
def signup():
    return render_template('signup.html', msg=None)

@app.route('/signup', methods=['POST'])
def signup_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        msg = "Signup successful! You can go back and login."
    except mysql.connector.Error:
        msg = "Error: Email already exists"
    finally:
        conn.close()

    return render_template('signup.html', msg=msg)

@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT m.id, m.content, m.user_id FROM messages m ORDER BY m.id ASC")
    messages = cursor.fetchall()

    cursor.execute("SELECT s.message_id, s.suggestion_text, s.suggested_by FROM suggestions s")
    suggestion_data = cursor.fetchall()
    conn.close()

    suggestions = {}
    for msg_id, text, suggester_id in suggestion_data:
        if msg_id not in suggestions:
            suggestions[msg_id] = []
        suggestions[msg_id].append((text, suggester_id))

    return render_template('welcome.html',
                           user_id=user_id,
                           messages=messages,
                           suggestions=suggestions)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    message = request.form['message']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_id, content) VALUES (%s, %s)", (user_id, message))
    conn.commit()
    conn.close()

    return redirect(url_for('welcome'))

@app.route('/send_suggestion', methods=['POST'])
def send_suggestion():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    suggestion_text = request.form['suggestion_text']
    message_id = request.form['message_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO suggestions (message_id, suggestion_text, suggested_by) VALUES (%s, %s, %s)",
                   (message_id, suggestion_text, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('welcome'))

@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM messages WHERE id = %s", (message_id,))
    result = cursor.fetchone()
    if result and result[0] == user_id:
        cursor.execute("DELETE FROM suggestions WHERE message_id = %s", (message_id,))
        cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('welcome'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Production mein debug mode hamesha False hona chahiye
    app.run(debug=False)
