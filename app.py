from threading import Lock
from flask import Flask, render_template, request
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
alone_user = []
partners = dict()


@app.route('/')
def orby():
    return render_template('daily.html', async_mode=socketio.async_mode)


# when a client connects
@socketio.on('connect')
def on_connect():
    emit('assign_user_id', request.sid, broadcast=False)

    if len(alone_user) > 1:
        print("SHOULD ONLY BE ONE ALONE USER")
        print(alone_user)

    print(alone_user)
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
        

# # when a client disconnects
@socketio.on('disconnect')
def disconnect():
    
    if partners[request.sid] is not None:
        prev_partner = partners[request.sid]
        del partners[request.sid]

        if alone_user == [None]:
            alone_user[-1] = prev_partner
            partners[prev_partner] = None
            emit('assign_partner', 0, room=prev_partner)
        elif alone_user == []:
            alone_user.append(prev_partner)
            partners[prev_partner] = None
            emit('assign_partner', 0, room=prev_partner)
        else:
            partner_id = alone_user.pop()
            emit('assign_partner', partner_id, room=prev_partner)
            emit('assign_partner', prev_partner, room=partner_id)
            partners[partner_id] = prev_partner
            partners[prev_partner] = partner_id

    if alone_user and request.sid == alone_user[-1]:
        alone_user.pop()

# when a client presses a key
@socketio.event
def client_keydown(radius):
    if partners[request.sid] is not None:
        emit('partner_state', (radius, "inhale"), room=partners[request.sid])

# when a client releases a key
@socketio.event
def client_keyup(radius):
    if partners[request.sid] is not None:
        emit('partner_state', (radius, "exhale"), room=partners[request.sid])


if __name__ == '__main__':
    socketio.run(app)
