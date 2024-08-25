from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

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
user_counts = {}

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         socketio.sleep(10)
#         count += 1
#         socketio.emit('my_response',
#                       {'data': 'Server generated event', 'count': count})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def ping():
    emit('pong')


# @socketio.event
# def my_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']})


# @socketio.event
# def my_broadcast_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          broadcast=True)


# @socketio.event
# def disconnect_request():
#     @copy_current_request_context
#     def can_disconnect():
#         disconnect()
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     # for this emit we use a callback function
#     # when the callback function is invoked we know that the message has been
#     # received and it is safe to disconnect
#     emit('my_response',
#          {'data': 'Disconnected!', 'count': session['receive_count']},
#          callback=can_disconnect)





# when a client connects
@socketio.on('connect')
def on_connect(message):
    # global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(background_thread)
    user_id = message['id']
    user_counts.update({user_id: 0})
    # send everyone new user list
    emit('add_user', user_counts, broadcast=True)



# when a client presses a key
@socketio.event
def client_keydown(message):
    user_id = message['data']
    # send everyone just this keypress update
    print({'user_id': user_id, 'key_state': "down"})
    emit('update_state', {'user_id': user_id, 'key_state': 'down'}, broadcast=True)

# when a client releases a key
@socketio.event
def client_keyup(message):
    user_id = message['data']
    # send everyone just this keypress update
    print({'user_id': user_id, 'key_state': "up"})
    emit('update_state', {'user_id': user_id, 'key_state': 'up'}, broadcast=True)


# when a client refreshes
@socketio.event
def disconnect():
    # disconnected_id = message['data']
    # user_counts.pop(disconnected_id)
    # send everyone new user list
    emit('user_disconnected', user_counts, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)
