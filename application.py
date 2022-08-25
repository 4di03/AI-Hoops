"""
Demo Flask application to test the operation of Flask with socket.io

Aim is to create a webpage that is constantly updated with random numbers from a background python process.

30th May 2014

===================

Updated 13th April 2018

+ Upgraded code to Python 3
+ Used Python3 SocketIO implementation
+ Updated CDN Javascript and CSS sources

"""




# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
from model.Game import Game
from model.objects import WIN_HEIGHT, WIN_WIDTH

__author__ = 'slynn'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

def randomNumberGenerator():
    """
    Generate a random number every 2 seconds and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    print("Making random numbers")
    while not thread_stop_event.isSet():
        number = round(random()*10, 3)
        print("number:" + str(number))
        socketio.emit('newnumber', {'number': number}, namespace='/menu')
        socketio.sleep(2)


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')


@app.route('/game/')
def game():
    socketio.emit('dimensions', [WIN_WIDTH, WIN_HEIGHT])
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('canvas.html')



@socketio.on('message', namespace='/menu')
def handle_message(data):
    print('received message: ' + data)
    socketio.emit('newnumber', {'number': 420}, namespace='/menu')


@socketio.on('connect', namespace='/menu')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)




@socketio.on('mode')
def prompt_mode(mode):
    #choose the gamemode for the game


    game = Game()

    if mode == "solo":
        game.play_solo(socketio)
        pass
    elif mode == "train":
        game.train_AI(socketio)
        pass
    elif mode == "winner":
        game.replay_genome(socketio)
        pass

@socketio.on('disconnect', namespace='/menu')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
