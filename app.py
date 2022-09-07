

# Start with a basic flask app webpage.
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from threading import Thread, Event
from model.Game import Game
from model.objects import WIN_HEIGHT, WIN_WIDTH
import json
import configparser
from flask_cors import CORS
app = Flask(__name__)

#CORS(app)

app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = False


game_mode= ""

config_data = {}


cfg_parser = configparser.ConfigParser()


cfg_parser.read("model/default_config.txt")


#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=False, engineio_logger=False,cors_allowed_origins="*")

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()



#creates config.txt from config object
def create_config_file(parser, config_data):
    # print(parser.sections())
    print(config_data)    
    for section in config_data:
        if section != "undefined":
            for key in config_data[section]:
                parser[section][key] = config_data[section][key]

        
    with open("model/config.txt", mode = "w") as cfg:

        #rewrite config into local file
        if config_data["undefined"]["config-file"] != "":
            parser = configparser.ConfigParser()
            parser.read(config_data["undefined"]["config-file"])

        parser.write(cfg)

        cfg.close()

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
    global game_mode
 
    game_mode = ""
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')


@app.route('/game/')
def game():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('canvas.html')


@app.route('/train/')
def train_menu():
    return render_template('train.html')


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)


@socketio.on("train_config")
def send_config(msg):
    global config_data

    config_data = json.loads(msg)

    create_config_file(cfg_parser, config_data)


    socketio.emit("confirm_config", "")


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

    print("GOT MODE: " + mode)
    game_mode = mode

    socketio.emit("got game", "")

@socketio.on('start')
def prompt_mode(waste):
    #choose the gamemode for the game
    socketio.emit('dimensions', json.dumps([WIN_WIDTH, WIN_HEIGHT]))

    game = Game(config_data["undefined"] if "undefined" in config_data else None, socketio)


    if game_mode == "solo":
        game.play_solo()
    elif game_mode == "train":
        game.train_AI()
    elif game_mode.split("/")[0] == "winner":

        if game_mode.split("/")[1] == "record":
            game.replay_genome()
        else:
            game.replay_genome(genome_path="model/local_winner.pkl")


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
    # app.run()