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
from  model.objects import WIN_HEIGHT, WIN_WIDTH, STAT_FONT, BALL_IMG, BALL_SIZE, BRAIN_BALL_IMG, BEST_BALL_IMG,  BG_IMG
import json 
import sys 
import random
import time
from flask import request, copy_current_request_context
# from application import config_data, create_config_file

socket = None

game_map = {}

DEFAULT_FPS = 250

CHOSEN_FPS = 100

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


    def __init__(self, custom_config, socketio, name = "no name"):
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

 
    
    def replay_local_genome(self):
        self.replay_genome(genome_path='model/local_winner.pkl')
    
    def replay_genome(self, framerate = DEFAULT_FPS, genome_path="model/best_winner.pkl"):
        # Load requried NEAT config
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

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
        self.config_path = "./model/config.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
            neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)
        

        p = neat.Population(config)


        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        def fast_main(genomes, config):
            self.main(genomes,config, framerate = CHOSEN_FPS)

        winner = p.run(self.main, self.max_gens)


        if self.override_winner and not self.kill:
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


        self.kill = False

    def emit_data(self,name, socket):

        balls_data = []
        for ball in self.balls:
            balls_data.append(ball.get_data())

        socket.emit(name,json.dumps(balls_data), to = request.sid)
        socket.sleep(0)


    def play_solo(self):
        Ball(self)
        self.solo = True
        self.main([],None)



    def main(self, genomes, config, framerate = DEFAULT_FPS, display = False):
        global game_map
        nets = []
        ge = []


        for genome_id , g in genomes:
            net = self.net_type.create(g, config)
            nets.append(net)
            Ball(self)
            g.fitness = 0
            ge.append(g)

        pyClock = pygame.time.Clock()
            
        run = len(self.balls)
        self.name = request.sid
        game_map[request.sid] = self

        last_time = time.time()

        frame_ct = 0


        while run:
            
            frame_ct += 1
            #time since last frame in frames to base game (250 fps)
            dt = (time.time() - last_time) * DEFAULT_FPS
            last_time = time.time()

            # print(f"running game for {request.sid}")
     
            global bboxes
            pyClock.tick(framerate)
            
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

            i = len(self.balls) - 1
            while i >= 0:

                ball = self.balls[i]

                ball.move(nets, ge , i, self, dt)

                i -= 1

            if (frame_ct % (int(framerate/CHOSEN_FPS))) == 0:
                self.emit_data("screen", socket)



            if len(self.balls) == 0:
                self.__init__(self.custom_config, socket)

                return
