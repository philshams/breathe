from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# this is the state of the app
# all events update and/or use this state
users_inhaling = set()
users_exhaling = set()

@app.route('/')
def orby():
    return render_template('orby.html', async_mode=socketio.async_mode)

@app.route('/together/')
def together():
    return render_template('together.html')

@app.route('/alone/')
def alone():
    return render_template('alone.html')

# when a client connects
@socketio.on('connect')
def on_connect():
    emit('assign_user_id', request.sid, broadcast=False)
    # send everyone new user list
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)

# when a client disconnects
@socketio.on('disconnect')
def disconnect():
    # disconnected_id = message['data']
    user_id = request.sid
    users_inhaling.discard(user_id)
    users_exhaling.discard(user_id)
    # send everyone new user list
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)

# when a client presses a key
@socketio.event
def client_keydown():
    user_id = request.sid
    users_inhaling.add(user_id)
    users_exhaling.discard(user_id)
    # send everyone just this keypress update
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)

# when a client releases a key
@socketio.event
def client_keyup():
    user_id = request.sid
    users_inhaling.discard(user_id)
    users_exhaling.add(user_id)
    # send everyone just this keypress update
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)

# when a client times out
@socketio.event
def timeout():
    user_id = request.sid
    users_inhaling.discard(user_id)
    users_exhaling.discard(user_id)
    # send everyone new user list
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)


# when a client refreshes or times out
@socketio.event
def leave():
    user_id = request.sid
    users_inhaling.discard(user_id)
    users_exhaling.discard(user_id)
    # send everyone new user list
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
