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
    return render_template('partner.html', async_mode=socketio.async_mode)

# when a client connects
@socketio.on('connect')
def on_connect():
    emit('assign_user_id', request.sid, broadcast=False)       


def _leave_room(user_id):
    if user_id in partners and partners[user_id] is not None:
        emit('end_session', {}, to = partners[user_id])
        del partners[user_id]

    if alone_user and user_id == alone_user[-1]:
        alone_user.pop()

    if alone_user and user_id in alone_user[-1] and user_id != alone_user[-1]:
        alone_user.remove(user_id)


# # when a client disconnects
@socketio.on('disconnect')
def disconnect():
    _leave_room(request.sid)

@socketio.event
def leave_room():
    _leave_room(request.sid)

@socketio.event
def join_room():
    if alone_user == [None]:
        alone_user[-1] = request.sid
        partners[request.sid] = None
    elif alone_user == []:
        alone_user.append(request.sid)
        partners[request.sid] = None
    else:
        partner_id = alone_user.pop()
        emit('assign_partner', partner_id, broadcast=False)
        emit('assign_partner', request.sid, room=partner_id)
        partners[partner_id] = request.sid
        partners[request.sid] = partner_id

# when a client presses a key
@socketio.event
def client_keydown(radius, time_in_session):
    if request.sid in partners and partners[request.sid] is not None:
        emit('partner_state', (radius, "inhale", time_in_session), room=partners[request.sid])

# when a client releases a key
@socketio.event
def client_keyup(radius, time_in_session):
    if request.sid in partners and partners[request.sid] is not None:
        emit('partner_state', (radius, "exhale", time_in_session), room=partners[request.sid])


if __name__ == '__main__':
    socketio.run(app)
