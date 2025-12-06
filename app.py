from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os


app = Flask(__name__)
app.secret_key = "secret123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))             # <-- ADD THIS
    room_code = db.Column(db.String(10), unique=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String, db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



with app.app_context():
    db.create_all()

@app.route("/", methods=["GET"])
def home():
    rooms = Room.query.order_by(Room.created_at.desc()).all()
    return render_template("index.html", rooms=rooms)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return f"Welcome {session['username']}!"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find user in DB
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # store login info in session
            session['user_id'] = user.id
            session['username'] = user.username
            
            return redirect(url_for('dashboard'))
        else:
            return "Invalid username or password"

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Save user to DB
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    user_rooms = Room.query.filter_by(created_by=user.id).all()

    return render_template("dashboard.html", user=user, user_rooms=user_rooms)




@app.route("/create_room", methods=["GET", "POST"])
def create_room():
    if request.method == "POST":
        room_name = request.form.get("room_name", "").strip() or "Untitled Room"
        room_code = str(uuid.uuid4())[:8]

        room = Room(
            name=room_name,
            room_code=room_code,
            created_by=session['user_id']
        )

        db.session.add(room)
        db.session.commit()

        return redirect(url_for("room", room_id=room.id))

    return render_template("create_room.html")

@app.route('/room/<room_id>')
def room(room_id):
    room = Room.query.get_or_404(room_id)
    messages = Message.query.filter_by(room_id=room_id).all()
    return render_template('room.html', room=room, messages=messages)


@app.route('/send_message/<room_id>', methods=['POST'])
def send_message(room_id):
    text = request.form['message']
    user_id = session['user_id']

    msg = Message(room_id=room_id, user_id=user_id, text=text)
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for('room', room_id=room_id))

@app.route('/upload/<room_id>', methods=['POST'])
def upload(room_id):
    file = request.files['file']
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    return redirect(url_for('room', room_id=room_id))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
