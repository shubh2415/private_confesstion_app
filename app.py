# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'secretkey' # Flash messages ke liye secret key zaroori hai

def get_db_connection():
    # Local machine setup ke liye database credentials seedhe daal rahe hain
    # 'your_password' ki jagah apna asli MySQL password daalein
    # 'defaultdb' ki jagah apne database ka naam daalein agar alag hai
    return mysql.connector.connect(
        host='localhost',    # Aapke MySQL server ka host, aksar 'localhost' hota hai
        user='root',         # Aapke MySQL user ka naam
        password='', # <-- Yahan apna MySQL password daalein
        database='defaultdb' # <-- Yahan apne database ka naam daalein
    )

@app.route('/')
def login():
    # Flash messages ko render karein
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
        flash("Invalid credentials. Please try again.", "error") # Error message for login
        return render_template('login.html') # Flash messages ke liye redirect na karein

@app.route('/signup')
def signup():
    return render_template('signup.html')

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
        # Signup successful hone par login page par redirect karein aur message flash karein
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))
    except mysql.connector.Error as err:
        if err.errno == 1062:
            flash("Error: Email already exists. Please use a different email.", "error")
        else:
            flash(f"An unexpected error occurred: {err}", "error")
    finally:
        conn.close()

    return render_template('signup.html') # Agar signup mein error aaye to signup page par hi rahe

@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.id, m.content, m.user_id FROM messages m
        ORDER BY m.id ASC
    """)
    messages = cursor.fetchall()

    cursor.execute("""
        SELECT s.message_id, s.suggestion_text, s.suggested_by FROM suggestions s
    """)
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

# Naya route description page ke liye
@app.route('/app_details')
def app_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('app_details.html')

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
    else:
        # User trying to delete someone else's message
        flash("You can only delete your own messages.", "error")

    conn.close()
    return redirect(url_for('welcome'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
