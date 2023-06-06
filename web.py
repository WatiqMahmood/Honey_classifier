from flask import Flask, redirect, render_template, request, url_for,session,flash
from PIL import Image, ImageDraw, ImageFont
from flask_mail import Mail, Message
import sqlite3
import torch
from createtable import user_exists

def register_user_to_db(username, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO users(username,password) values (?,?)', (username, password))
    con.commit()
    con.close()

def check_user(username, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('Select username,password FROM users WHERE username=? and password=?', (username, password))

    result = cur.fetchone()
    if result:
        return True
    else:
        return False

app = Flask(__name__)
app.secret_key = "r@nd0mSk_1"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'amnadilawar14@gmail.com'  # Your Gmail email address
app.config['MAIL_PASSWORD'] = 'wsoounehkvbrtuop'  # Your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'amnadilawar14@gmail.com'  # Your Gmail email address
mail = Mail(app)

# Load the YOLOv7 model
model = torch.hub.load('WongKinYiu/yolov7', 'custom', 'best.pt')
model.eval()

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/login')
def index1():
    return render_template('login.html')


@app.route('/classification')
def classification():
    return render_template('classification.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Create and send the email
        msg = Message('Honey Classifier', sender='amnadilawar14@gmail.com', recipients=['amnadilawar14@gmail.com'])
        msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)

        flash('Your message has been sent!', 'success')
        return redirect('/contact')

    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if user_exists(username):
            flash('User already exists. Please choose a different username.', 'error')
            return render_template('register.html')
        else:
            register_user_to_db(username, password)
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('register'))

    else:
        return render_template('register.html')
    
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(check_user(username, password))
        if check_user(username, password):
            session['username'] = username

        return redirect(url_for('home'))
    else:
        return redirect(url_for('index'))
    
@app.route('/home', methods=['POST', "GET"])
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        error_message = 'Invalid username or password.'
        return render_template('login.html', error_message=error_message)
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/detect', methods=['POST'])
def detect():
    # Get the uploaded image from the request
    image = request.files['image']
    img = Image.open(image)

    # Get the predictions
    results = model(img)

    # Extract the bounding boxes, labels, and scores
    boxes = results.xyxy[0].tolist()
    labels = results.names[0]
    scores = results.xyxy[0][:, 4].tolist()

    total_detections = len(boxes)

    # Count the detections for each class
    class_counts = {}
    for label in labels:
        class_counts[label] = 0

    for label_index in results.pred[0][:, -1].tolist():
        class_counts[labels[int(label_index)]] += 1

    # Calculate the percentage of detections for each class
    class_percentages = {label: count / total_detections * 100 for label, count in class_counts.items()}

    # Create the detection report
    detection_report = []
    detection_report.append("A ---> Acecia")
    detection_report.append("a ---> Wold_Flower")
    detection_report.append("c ---> Sidr ")
    detection_report.append("i ---> Trifoleum")
    detection_report.append(f"Total Detections: {total_detections}")

    for label, count in class_counts.items():
        percentage = class_percentages[label]
        detection_report.append(f"{label}: Count={count}, Percentage={percentage:.2f}%")

    # Plot the image and bounding boxes
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 40)
    my_list = [i for i in class_counts.values()]
    if my_list[0] > my_list[1] and my_list[0] > my_list[2] and my_list[0] > my_list[3]:
        detection_report.append("This honey is Acecia honey")
    elif my_list[1] > my_list[0] and my_list[1] > my_list[2] and my_list[1] > my_list[3]:
        detection_report.append("This honey is Sidr honey")
    elif my_list[3] > my_list[0] and my_list[3] > my_list[1] and my_list[3] > my_list[2]:
        detection_report.append("This honey is Trifoleum honey")

    for box, score, label_index in zip(boxes, scores, results.pred[0][:, -1].tolist()):
        xmin, ymin, xmax, ymax = box[:4]
        label = f"{labels[int(label_index)]} {score:.2f}"
        draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="red", width=6)
        draw.text((xmin, ymin - 40), label, font=font, fill="red")


    # Save the annotated image
    img_path = 'static/result.jpg'
    img.save(img_path)

    return render_template('report.html', img_path=img_path, detection_report=detection_report)

if __name__ == '__main__':
    app.run(debug=True)
