from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from datetime import datetime



app = Flask(__name__)
app.secret_key = "secret123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


os.makedirs(UPLOAD_FOLDER, exist_ok=True)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(10), unique=True)
    pomodoro_enabled = db.Column(db.Boolean, default=False)
    
   

    pomodoro_state = db.Column(db.String(20), default="stopped")

    pomodoro_end_time = db.Column(db.DateTime, nullable=True)

    pomodoro_focus_minutes = db.Column(db.Integer, default=25)
    pomodoro_break_minutes = db.Column(db.Integer, default=5)


    room_type = db.Column(db.String(20))
    level = db.Column(db.String(20))
    capacity = db.Column(db.Integer)

    chat_type = db.Column(db.String(20))
    file_upload = db.Column(db.String(5))
    voice_chat = db.Column(db.String(5))

    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    extras = db.Column(db.String(200))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')

    
class RoomMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable = False)
    status = db.Column(db.String(20), default="online")
    
class RoomFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    with app.app_context():
        db.create_all()

    



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
        pomodoro = request.form.get("pomodoro") == "on"

        room = Room(
            room_code=str(uuid.uuid4())[:6],
            room_type=request.form.get("room_type"),
            level=request.form.get("level"),
            capacity=request.form.get("capacity"),

            chat_type=request.form.get("chat_type"),
            file_upload=request.form.get("file_upload"),
            voice_chat=request.form.get("voice_chat"),
            extras=request.form.get("extras"),
            pomodoro_enabled=pomodoro,

            created_by=session.get("user_id")
        )

        db.session.add(room)
        db.session.commit()

        return redirect(url_for("room", room_code=room.room_code))

    return render_template("create_room.html")






@app.route("/room/<room_code>")
def room(room_code):
    room = Room.query.filter_by(room_code=room_code).first_or_404()
    files = RoomFile.query.filter_by(room_id=room.id).all()


    members = (
        db.session.query(User.username, RoomMember.status)
        .join(RoomMember, RoomMember.user_id == User.id)
        .filter(RoomMember.room_id == room.id)
        .all()
    )

    return render_template(
        "room.html",
        room=room,
        members=members,
        files=files
    )


@app.route("/room/<room_code>/timer")
def get_timer(room_code):
    room = Room.query.filter_by(room_code=room_code).first()

    if not room.pomodoro_end_time:
        return {"state": "stopped", "remaining": 0}

    remaining = int((room.pomodoro_end_time - datetime.utcnow()).total_seconds())

    if remaining < 0:
        remaining = 0

    return {
        "state": room.pomodoro_state,
        "remaining": remaining
    }

@app.route("/room/<room_code>/send_message", methods=["POST"])
def send_message(room_code):
    room = Room.query.filter_by(room_code=room_code).first_or_404()

    text = request.form.get("message")
    user_id = session.get("user_id")

    if not text:
        return "Empty", 400

    msg = Message(room_id=room.id, user_id=user_id, text=text)
    db.session.add(msg)
    db.session.commit()

    return "OK"

@app.route("/room/<room_code>/messages")
def get_messages(room_code):
    room = Room.query.filter_by(room_code=room_code).first_or_404()

    msgs = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp).all()

    return jsonify([
        {
            "user": m.user.username,
            "text": m.text,
            "time": m.timestamp.strftime("%H:%M")
        } for m in msgs
    ])




@app.route('/send_message/<room_id>', methods=['POST'])
def room_message(room_id):
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

@app.route("/join_room", methods=["GET", "POST"])
def join_room():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        room_code = request.form.get("room_code").strip()

        room = Room.query.filter_by(room_code=room_code).first()
        if not room:
            return render_template(
                "join_room.html",
                error="Room not found"
            )

        # check if already joined
        existing = RoomMember.query.filter_by(
            user_id=session["user_id"],
            room_id=room.id
        ).first()

        if not existing:
            member = RoomMember(
                user_id=session["user_id"],
                room_id=room.id
            )
            db.session.add(member)
            db.session.commit()

        return redirect(url_for("room", room_code=room.room_code))

    return render_template("join_room.html")

from werkzeug.utils import secure_filename

@app.route("/upload_file/<int:room_id>", methods=["POST"])
def upload_file(room_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    file = request.files.get("file")
    if not file or file.filename == "":
        return redirect(request.referrer)

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    room_file = RoomFile(
        filename=filename,
        room_id=room_id,
        uploaded_by=session["user_id"]  # ✅ FIX
    )

    db.session.add(room_file)
    db.session.commit()

    room = db.session.get(Room, room_id)
    return redirect(url_for("room", room_code=room.room_code))


@app.route("/files/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)






@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
