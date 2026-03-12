from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

waiting_user = None
partners = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join():
    global waiting_user
    if waiting_user is None:
        waiting_user = request.sid
        emit('waiting', {'msg': 'Stranger dhundh rahe hain...'})
    else:
        partner = waiting_user
        waiting_user = None
        partners[request.sid] = partner
        partners[partner] = request.sid
        emit('connected', {'msg': 'Stranger mil gaya! Baat karo 😊'})
        emit('connected', {'msg': 'Stranger mil gaya! Baat karo 😊'}, to=partner)

@socketio.on('message')
def on_message(data):
    partner = partners.get(request.sid)
    if partner:
        emit('message', {'msg': data['msg'], 'user': 'Stranger'}, to=partner)
        emit('message', {'msg': data['msg'], 'user': 'Tum'})

@socketio.on('image')
def on_image(data):
    partner = partners.get(request.sid)
    if partner:
        emit('image', {'img': data['img'], 'user': 'Stranger'}, to=partner)
        emit('image', {'img': data['img'], 'user': 'Tum'})

@socketio.on('webrtc_offer')
def on_offer(data):
    partner = partners.get(request.sid)
    if partner:
        emit('webrtc_offer', data, to=partner)

@socketio.on('webrtc_answer')
def on_answer(data):
    partner = partners.get(request.sid)
    if partner:
        emit('webrtc_answer', data, to=partner)

@socketio.on('webrtc_ice')
def on_ice(data):
    partner = partners.get(request.sid)
    if partner:
        emit('webrtc_ice', data, to=partner)

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

@socketio.on('typing')
def on_typing():
    partner = partners.get(request.sid)
    if partner:
        emit('typing', {}, to=partner)

@socketio.on('stop_typing')
def on_stop_typing():
    partner = partners.get(request.sid)
    if partner:
        emit('stop_typing', {}, to=partner)

@socketio.on('disconnect')
def on_disconnect():
    global waiting_user
    partner = partners.get(request.sid)
    if partner:
        emit('disconnected', {'msg': 'Stranger ne connection tod diya! 😢'}, to=partner)
        partners.pop(partner, None)
    partners.pop(request.sid, None)
    if waiting_user == request.sid:
        waiting_user = None

if __name__ == '__main__':
    socketio.run(app, debug=True)