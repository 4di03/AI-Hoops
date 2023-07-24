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
from flask_socketio import SocketIO
from flask import request, copy_current_request_context
from abc import ABC, abstractmethod
sys.path.append('./model')
from ReportingPopulation import ReportingPopulation
sys.path.append('./util')
from util import ScreenDataEmitter
# from application import config_data, create_config_file
#
# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=0, stdoutToServer=True, stderrToServer=True)

socket = None

game_map = {}

GAME_FRAMERATE = 200

CHOSEN_FPS = TICKS_PER_SEC

#only for solo mode
def make_move(input):


    msg,sid= input.split("#")
    game = game_map[sid]


    # print(f'trying to move, SID: {sid}, request.id: {request.sid}, game: {game}, true game socketid: {game.name}')
    if sid == request.sid and sid == game.name and game.solo:
        if msg == "right" and len(game.balls) > 0:
            game.balls[0].jump(True)

        elif msg == "left" and len(game.balls) > 0:
            game.balls[0].jump(False)


class Game:
    config_path = "./model/config.txt"


    def __init__(self, custom_config, socketio : SocketIO,name = "no name", framerate = GAME_FRAMERATE):
        '''
        args:
            framerate: How frequently
            TODO: move custom_config to controller, model should not know if visuals are sent to the view
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
        self.max_gens = None
        self.graphics = True
        self.override_winner = False
        if custom_config:
            self.max_gens = int(custom_config["max_gens"])
            if "Feed-Forward NN" in custom_config:
                self.net_type = neat.nn.FeedForwardNetwork
            else: 
                self.net_type = neat.nn.RecurrentNetwork

            self.graphics = custom_config["graphics_choice"] == "true"
            self.override_winner = custom_config["winner_choice"] == "true"

            self.custom_config = custom_config
        else:
            self.custom_config = None

        self.framerate = framerate

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

        pyClock.tick(TICKS_PER_SEC)

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
    def __init__(self, game):

        self.game = game


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
        self.main(genomes, config)


    

    def show_train(self):
        self.train_AI(True)

    def show_main(self, genomes, config):
        raise Exception("GRAPHICS MODE")
        self.main(genomes,config)
    def train_AI(self):
        self.game.config_path = "./model/config.txt"
        graphics = False#self.game.graphics TRYING THISs

        #self.game.graphics = True # only THIS DOES

        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
            neat.DefaultSpeciesSet, neat.DefaultStagnation, self.game.config_path)
        
        #p = neat.Population(config) if self.game.graphics else ReportingPopulation(config, socket) # emit data to client if graphics is true, else emit stdout
        p = ReportingPopulation(config, socket, graphics) # emit data to client if graphics is true, else emit stdout, NOT CULPRIT


        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        # def fast_main(genomes, config):
        #     self.main(genomes,config, framerate = CHOSEN_FPS)

        mfunc = self.main # decides whether to show graphics or not
        winner = p.run(mfunc, self.game.max_gens)


        if self.game.override_winner and not self.game.kill:
            print("overriding local winner")
            with open("model/local_winner.pkl", "wb") as f:
                pickle.dump(winner, f)
                f.close()

            cur_highscore = int(open("model/highscore.txt", mode="rt").read())
            if winner.fitness > cur_highscore:
                with open("model/highscore.txt", mode = "w") as h:
                    h.write(str(winner.fitness))
                
                print("overriding record winner")

                with open("model/best_winner.pkl", "wb") as f:
                    pickle.dump(winner, f)
                    f.close()


        self.game.kill = False


    def play_solo(self):
        Ball(self.game)
        self.game.solo = True
        self.main([],None)


    def main(self, genomes, config):
        '''
        main method for the game, runs the game loop and emits screen data to client
        args:
            display: whether or not to emit screen data to client, if False, emit stdout string buffer to client
        '''
        global game_map
        nets = [] # list of neural networks
        ge = [] # list of genomes
        display = self.game.graphics


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

        emit_name = 'screen' #if not display else 'screen'


        emitter = ScreenDataEmitter(self.game, name = emit_name)
        while run:  
            #print(len(self.game.balls))
            if len(self.game.balls) == 0:
                return  # end the game if no balls on screen
            last_time = time.time()
            tick_ct += 1

            self.game.run_frame(pyClock, nets , ge, last_time = last_time)
            socket.on_event('input', make_move) # non-decorator version of socket.on

            @socket.on('quit')
            def quit_game(sid):
                # print(f'trying to quit, SID: {sid}, request.id: {request.sid}, game: {self}, true game socketid: {self.name}')

                if sid in game_map:
                    game = game_map[sid]
                    if sid == request.sid and sid == game.name:
                        # print("Quitting for " + sid +", " + str(self))
                        if ge:
                            ge[0].fitness = sys.maxsize
                            game.kill = True
                        game.balls = []


            skip_frames = round(TICKS_PER_SEC/self.game.framerate)



            if (tick_ct % skip_frames) == 0 and display: #only emit data for self.game.framerate frames per second TRYNG THIS

                emitter.emit_data(socket= socket)
            
                # socket.emit(emit_name, self.game.graphics, to = request.sid)
                # socket.sleep(0)

            socket.sleep(0)# per https://stackoverflow.com/questions/55503874/flask-socketio-eventlet-error-client-is-gone-closing-socket



