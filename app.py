from threading import Lock
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import os

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
alone_user = []
partners = dict()


@app.route('/')
def meditate():
    return render_template('meditate.html', async_mode=socketio.async_mode)

@app.route('/solo')
def solo():
    return render_template('solo.html', async_mode=socketio.async_mode)

@app.route('/partner')
def partner():
    room_id = os.urandom(4).hex()
    return render_template('partner.html', room_id=room_id, async_mode=socketio.async_mode)

@app.route('/room/<room_id>')
def room(room_id):
    return render_template('meditate.html', room_id=room_id, async_mode=socketio.async_mode)

# when a client connects
@socketio.on('connect')
def on_connect():
    emit('assign_user_id', request.sid, broadcast=False)       


def _leave_room(user_id):
    for room_id, users in list(rooms.items()):
        if user_id in users:
            users.remove(user_id)
            if not users:
                del rooms[room_id]


# # when a client disconnects
@socketio.on('disconnect')
def disconnect():
    _leave_room(request.sid)

@socketio.event
def leave_room():
    _leave_room(request.sid)

from flask_socketio import join_room, leave_room as leave_socket_room
rooms = {}  # room_id → [user_ids]

@socketio.event
def join_room_event(data):
    room_id = data['room']
    if room_id in rooms and len(rooms[room_id]) > 1:
    # room full -> send redirect message
        emit('room_full', {'msg': "Sorry, the room you entered is already full."}, room=request.sid)
        return
    join_room(room_id)
    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(request.sid)
    if len(rooms[room_id]) == 2:
        for uid in rooms[room_id]:
            partner_id = [x for x in rooms[room_id] if x != uid][0]
            emit('assign_partner', partner_id, to=uid)



@socketio.event
def client_keydown(radius, time_in_session, room):
    emit('partner_state', (radius, "inhale", time_in_session), to=room, include_self=False)

@socketio.event
def client_keyup(radius, time_in_session, room):
    emit('partner_state', (radius, "exhale", time_in_session), to=room, include_self=False)

if __name__ == '__main__':
    socketio.run(app)
