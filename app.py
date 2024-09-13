from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a real secret key

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sat123@@'
app.config['MYSQL_DB'] = 'quiz_app_1'
mysql = MySQL(app)

# Email configuration
EMAIL_ADDRESS = 'sathishns035@gmail.com'  # Your email
EMAIL_PASSWORD = 'swdnmhvscoviafyz'  # Your email password

# Send quiz results to user and admin
def send_results(email, username, score, total):
    admin_email = 'sathishns035@gmail.com'
    subject = 'Quiz Results'
    body = f"""
    Hi {username},

    Your quiz results:
    Score: {score}/{total}

    Regards,
    Quiz Team
    """

    admin_body = f"""
    Admin Notification:

    User Email: {email}
    Username: {username}
    Score: {score}/{total}
    """

    # Send email to user
    msg_user = MIMEMultipart()
    msg_user['From'] = EMAIL_ADDRESS
    msg_user['To'] = email
    msg_user['Subject'] = subject
    msg_user.attach(MIMEText(body, 'plain'))

    # Send email to admin
    msg_admin = MIMEMultipart()
    msg_admin['From'] = EMAIL_ADDRESS
    msg_admin['To'] = admin_email
    msg_admin['Subject'] = subject
    msg_admin.attach(MIMEText(admin_body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            # Send email to user
            server.send_message(msg_user)
            # Send email to admin
            server.send_message(msg_admin)
            print("Emails sent successfully!")
    except Exception as e:
        print(f"Failed to send emails: {e}")

@app.route('/')
@app.route('/login')
def home():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("SELECT password, email FROM users WHERE username=%s OR email=%s", (username, username))
    user = cursor.fetchone()
    if user and check_password_hash(user[0], password):
        session['username'] = username
        session['email'] = user[1]  # Store email in session
        return redirect(url_for('quiz'))
    return 'Login Failed'

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    mobile = request.form['mobile']
    college = request.form['college']
    password = generate_password_hash(request.form['password'])
    conn = mysql.connection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, email, mobile, college, password) VALUES (%s, %s, %s, %s, %s)",
                   (username, email, mobile, college, password))
    conn.commit()
    return redirect(url_for('home'))

@app.route('/quiz')
def quiz():
    if 'username' in session:
        return render_template('quiz.html')
    return redirect(url_for('home'))

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'username' in session:
        # Get the answers submitted
        answers = request.form
        correct_answers = {
            'q1': 'Paris',
            'q2': '4',
            'q3': 'William Shakespeare',
            'q4': 'Mars',
            'q5': '100°C'
        }
        score = 0
        total = len(correct_answers)

        # Calculate the score
        for question, correct_answer in correct_answers.items():
            if answers.get(question) == correct_answer:
                score += 1

        # Get the current user's username and email
        username = session['username']
        email = session['email']

        # Store the quiz results in the database
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("INSERT INTO quiz_results (username, email, score, total) VALUES (%s, %s, %s, %s)",
                       (username, email, score, total))
        conn.commit()

        # Send quiz results to both user and admin
        send_results(email, username, score, total)

        return f"Your score is {score}/{total}. Results saved and emailed successfully!"
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)