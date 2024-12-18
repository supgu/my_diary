from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        db='daily_diary',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user['id']
                    return redirect(url_for('diary'))
        finally:
            conn.close()
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                return redirect(url_for('login'))
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                title = request.form['title']
                content = request.form['content']
                cursor.execute("INSERT INTO diaries (user_id, title, content) VALUES (%s, %s, %s)", (user_id, title, content))
                conn.commit()

            cursor.execute("SELECT * FROM diaries WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
            diaries = cursor.fetchall()
    finally:
        conn.close()

    return render_template('diary.html', diaries=diaries)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
