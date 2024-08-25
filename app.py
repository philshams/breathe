from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

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
users_online = set()


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


# when a client connects
@socketio.on('connect')
def on_connect(message):
    user_id = message['id']
    users_online.add(user_id)
    # send everyone new user list
    emit('user_connection', list(users_online), broadcast=True)


# when a client presses a key
@socketio.event
def client_keydown(message):
    user_id = message['data']
    users_inhaling.add(user_id)
    users_exhaling.discard(user_id)
    # send everyone just this keypress update
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)

# when a client releases a key
@socketio.event
def client_keyup(message):
    user_id = message['data']
    users_inhaling.discard(user_id)
    users_exhaling.add(user_id)
    # send everyone just this keypress update
    emit('update_state', {'inhaling': list(users_inhaling), 'exhaling': list(users_exhaling)}, broadcast=True)


# when a client refreshes
@socketio.event
def leave(message):
    user_id = message['data']
    users_inhaling.discard(user_id)
    users_exhaling.discard(user_id)
    users_online.discard(user_id)
    # send everyone new user list
    emit('user_connection', list(users_online), broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
