import re
import eventlet
eventlet.monkey_patch()
from lib2to3.pytree import generate_matches
from socket import socketpair
import pygame
import os
pygame.font.init()
import neat
import pickle
from model.objects import Ball
from model.Image import Image, Button
from  model.objects import WIN_HEIGHT, WIN_WIDTH, STAT_FONT, BALL_IMG, BALL_SIZE, BRAIN_BALL_IMG, BEST_BALL_IMG,  BG_IMG, TICKS_PER_SEC
import json 
import sys 
import random
import time
from flask import request, copy_current_request_context
from abc import ABC, abstractmethod
# from application import config_data, create_config_file

socket = None

game_map = {}


class DataEmitter(ABC):
    '''
    Abstract FunctionObject for emitting json data 
    of a certain type from server to client.
    '''

    def __init__(self,game, name, socket):
        '''
        args:
            game: an instance of Game
            name: name of even to emit to client
        '''
        self.game = game
        self.name = name

    @abstractmethod
    def get_data(self):
        '''
        returns json data to emit to client
        args:  
            game: an instance of Game
        '''
        raise NotImplementedError

    def emit_data(self,socket):
        '''
        emits data to client.
        args:
            name: name of event to emit to client
            socket: SocketIO object
            game: Game object
        '''
        socket.emit(self.name,self.get_data(), to = request.sid)
        socket.sleep(0)


class ScreenDataEmitter(DataEmitter):


    def get_data(self):
        '''
        Gets jsonified screen data to emit to client
        '''
        balls_data = []
        for ball in self.game.balls:
            balls_data.append(ball.get_data())

        return json.dumps(balls_data)


class StdoutDataEmitter(DataEmitter):

    def get_data(self):
        '''
        Get data from server stdout as string into json format
        '''

        return json.dumps(sys.stdout.getvalue())

CHOSEN_FPS = TICKS_PER_SEC

#only for solo mode
def make_move(input):
    input,sid= input.split("#")
    game = game_map[sid]

    # print(f'trying to move, SID: {sid}, request.id: {request.sid}, game: {game}, true game socketid: {game.name}')
    if sid == request.sid and sid == game.name and game.solo:
        if input == "right" and len(game.balls) > 0:
            game.balls[0].jump(True)

        elif input == "left" and len(game.balls) > 0:
            game.balls[0].jump(False)


class Game:
    config_path = "./model/config.txt"


    def __init__(self, custom_config, socketio,name = "no name"):
        '''
        args:
            framerate: How frequently
        '''
        global socket
        self.name = name
        self.balls = []
        self.images = []
        self.show_display_options = False
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        self.kill = False
        self.net_type = neat.nn.FeedForwardNetwork
        socket = socketio
        self.solo = False
        if custom_config:
            self.max_gens = int(custom_config["max_gens"])
            if "Feed-Forward NN" in custom_config:
                self.net_type = neat.nn.FeedForwardNetwork
            else: 
                self.net_type = neat.nn.RecurrentNetwork

            self.graphics = custom_config["graphics_choice"] == "on"
            self.override_winner = custom_config["winner_choice"] == "on"
            self.custom_config = custom_config
        else:
            self.custom_config = None



        self.gen = 0

    def run_frame(self, pyClock, nets, ge, last_time = 0):
        '''
        Moves all balls in game in a single frame
        args:
            pyClock: pygame clock object
            nets: list of neural networks
            ge: list of genomes
        '''

        if len(self.balls) == 0:
            self.__init__(self.custom_config, socket)

            return

        #time since last tick in ticks to base game (250 fps)
        dt = (time.time() - last_time) * TICKS_PER_SEC 

        # print(f"running game for {request.sid}")
    
        

        i = len(self.balls) - 1
        while i >= 0:

            ball = self.balls[i]

            ball.move(nets, ge , i, self, dt)

            i -= 1


class GameController:
    '''
    Controller for Game object, runs the game , takes input, and runs NEAT after every frame.
    '''
    def __init__(self, game, framerate = TICKS_PER_SEC):

        self.game = game

        self.framerate = framerate

    def replay_local_genome(self):
        self.replay_genome(genome_path='model/local_winner.pkl')
    
    def replay_genome(self, framerate = TICKS_PER_SEC, genome_path="model/best_winner.pkl"):
        # Load requried NEAT config
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                    neat.DefaultSpeciesSet, 
                                    neat.DefaultStagnation, 
                                    self.game.config_path)

        # Unpickle saved winner
        with open(genome_path, "rb") as f:
            genome = pickle.load(f)

        # Convert loaded genome into required data structure
        genomes = [(1, genome)]

        # Call game with only the loaded genome
        self.main(genomes, config, framerate,socket)


    

    def show_train(self):
        self.train_AI(True)

    def show_main(self, genomes, config):
        self.main(genomes,config,display= True)


    def train_AI(self, display = False):
        self.game.config_path = "./model/config.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
            neat.DefaultSpeciesSet, neat.DefaultStagnation, self.game.config_path)
        

        p = neat.Population(config)


        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        # def fast_main(genomes, config):
        #     self.main(genomes,config, framerate = CHOSEN_FPS)

        winner = p.run(self.main, self.game.max_gens)


        if self.game.override_winner and not self.game.kill:
            print("overriding local winner")
            with open("model/local_winner.pkl", "wb") as f:
                pickle.dump(winner, f)
                f.close()

            cur_highscore = int(open("model/highscore.txt", mode="rt").read())
            if winner.fitness > cur_highscore:
                with open("model/highscore.txt", mode = "w") as h:
                    h.write(winner.fitness)
                
                print("overriding record winner")

                with open("model/best_winner.pkl", "wb") as f:
                    pickle.dump(winner, f)
                    f.close()


        self.game.kill = False


    def play_solo(self):
        Ball(self.game)
        self.game.solo = True
        self.main([],None)


    def main(self, genomes, config,  display = True):
        '''
        main method for the game, runs the game loop and emits screen data to client
        args:
            display: whether or not to emit screen data to client, if False, emit stdout string buffer to client
        '''
        global game_map
        nets = [] # list of neural networks
        ge = [] # list of genomes

        for genome_id , g in genomes:
            net = self.game.net_type.create(g, config)
            nets.append(net)
            Ball(self.game)
            g.fitness = 0
            ge.append(g)

        pyClock = pygame.time.Clock()
            
        run = len(self.game.balls)
        self.game.name = request.sid
        game_map[request.sid] = self.game
        tick_ct = 0


        while run:
            last_time = time.time()
            tick_ct += 1

            self.game.run_frame(pyClock, nets , ge, last_time = last_time)

            socket.on_event('input', make_move)

            @socket.on('quit')
            def quit_game(sid):
                # print(f'trying to quit, SID: {sid}, request.id: {request.sid}, game: {self}, true game socketid: {self.name}')
                game = game_map[sid]
                if sid == request.sid and sid == game.name:
                    # print("Quitting for " + sid +", " + str(self))
                    if ge:
                        ge[0].fitness = sys.maxsize
                        game.kill = True
                    game.balls = []

            if display and (tick_ct % (int(TICKS_PER_SEC/self.framerate))) == 0: #only emit data for self.game.framerate frames per second
                emit_name = 'screen'

                emitter = ScreenDataEmitter(self.game, name = emit_name)
            elif not display:
                emit_name = 'stdout'

                emitter = StdoutDataEmitter(self.game, name = emit_name)
            
            emitter.emit_data(socket= socket, name = emit_name)

