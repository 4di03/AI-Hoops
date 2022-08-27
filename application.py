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
import json

__author__ = 'slynn'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True


game_mode= "solo"

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
        socketio.emit('newnumber', {'number': number})
        socketio.sleep(2)


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')


@app.route('/game/')
def game():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('canvas.html')



@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    socketio.emit('newnumber', {'number': 420})


@socketio.on('connect')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Not Starting Thread")
        #thread = socketio.start_background_task(randomNumberGenerator)


@socketio.on('recieve_mode')
def recieve_mode(mode):
    global game_mode 


    game_mode = mode

@socketio.on('start')
def prompt_mode(waste):
    #choose the gamemode for the game
    socketio.emit('dimensions', json.dumps([WIN_WIDTH, WIN_HEIGHT]))

    game = Game()

    print("GAME STARTED")

    if game_mode == "solo":
        game.play_solo(socketio)
        pass
    elif game_mode == "train":
        game.train_AI(socketio)
        pass
    elif game_mode == "winner":
        game.replay_genome(socketio)
        pass

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
