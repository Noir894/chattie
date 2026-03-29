from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey123'
socketio = SocketIO(app)

# ✅ FIXED USER DB (IMPORTANT)
users = {
    "test": generate_password_hash("123")
}

waiting_user = None
partners = {}

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return "User already exists"

        users[username] = generate_password_hash(password)
        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_password = users.get(username)

        if user_password and check_password_hash(user_password, password):
            session['user'] = username
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')


@socketio.on('join')
def on_join():
    global waiting_user

    user = session.get('user')
    if not user:
        return

    if waiting_user is None:
        waiting_user = request.sid
        emit('waiting', {'msg': f'{user}, stranger dhundh rahe hain...'})
    else:
        partner = waiting_user
        waiting_user = None

        partners[request.sid] = partner
        partners[partner] = request.sid

        emit('connected', {'msg': 'Stranger mil gaya!'} )
        emit('connected', {'msg': 'Stranger mil gaya!'}, to=partner)


@socketio.on('message')
def on_message(data):
    partner = partners.get(request.sid)
    if partner:
        msg = data.get('msg', '').strip()
        if not msg:
            return

        emit('message', {'msg': msg, 'user': 'Stranger'}, to=partner)
        emit('message', {'msg': msg, 'user': 'Tum'})


@socketio.on('next')
def on_next():
    global waiting_user

    partner = partners.get(request.sid)

    if partner:
        emit('disconnected', {'msg': 'Stranger chala gaya!'}, to=partner)
        partners.pop(partner, None)

    partners.pop(request.sid, None)
    waiting_user = None

    emit('waiting', {'msg': 'Naya stranger dhundh rahe hain...'})


if __name__ == '__main__':
    socketio.run(app, debug=True)