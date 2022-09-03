from lib2to3.pytree import generate_matches
from socket import socketpair
from tkinter.messagebox import YES
import pygame
import time
import os
import random
pygame.font.init()
import neat
import pickle
from model.objects import Ball
from model.Image import Image, Button
from  model.objects import WIN_HEIGHT, WIN_WIDTH, STAT_FONT, BALL_IMG, BALL_SIZE, BRAIN_BALL_IMG, BEST_BALL_IMG,  BG_IMG
import json 
import socketio
import sys
# from application import config_data, create_config_file



socket = None


class Game:
    config_path = "./model/config.txt"


    def __init__(self, custom_config):
        self.balls = []
        self.images = []
        self.show_display_options = False
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        self.kill = False
        self.custom_config = custom_config
        self.max_gens = int(custom_config["max_gens"])
        if "Feed-Forward NN" in custom_config:
            self.net_type = neat.nn.FeedForwardNetwork
        else: 
            self.net_type = neat.nn.RecurrentNetwork

        self.graphics = custom_config["graphics_choice"] == "on"
        self.override_winner = custom_config["winner_choice"] == "on"
        self.gen = 0
        self.custom_config = custom_config
        print(self.net_type)
 
        
    
    def replay_genome(self,  socket, ticks = 250, genome_path="model/best_winner.pkl"):
        # Load requried NEAT config
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

        # Unpickle saved winner
        with open(genome_path, "rb") as f:
            genome = pickle.load(f)

        # Convert loaded genome into required data structure
        genomes = [(1, genome)]

        # Call game with only the loaded genome
        self.main(genomes, config, ticks,socket)


    

    def show_train(self):
        self.train_AI(True)

    def show_main(self, genomes, config):
        self.main(genomes,config,display= True)


    def train_AI(self, socketio, display = False):
        global socket

        socket= socketio

        self.config_path = "./model/config.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
            neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)
        

        p = neat.Population(config)


        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(self.main, self.max_gens)

        

        @socket.on('quit')
        def quit_train(msg):
            print("QUITTING TRIANINGS")
            quit()
        if self.override_winner and not self.kill:
            with open("local_winner.pkl", "wb") as f:
                pickle.dump(winner, f)
                f.close()

        self.kill = False


    def emit_data(self,name, socket):
        balls_data = []
        for ball in self.balls:
            balls_data.append(ball.get_data())

        socket.emit(name,json.dumps(balls_data))

    def play_solo(self, socketio):
        global socket
        print("PLAYING SOLO")
        Ball(self)
        socket = socketio
        self.main([],None,250)



    def main(self, genomes, config, ticks = 250, display = False):
        nets = []
        ge = []


        for genome_id , g in genomes:
            net = self.net_type.create(g, config)
            nets.append(net)
            Ball(self)
            g.fitness = 0
            ge.append(g)


        print(len(nets))

        time = pygame.time.Clock()
            
        run = len(self.balls)
        while run:
            global bboxes
            time.tick(ticks)
            
            if len(nets) == 0 and len(ge) == 0:
                @socket.on('input')
                def make_move(input):
                    if input == "right" and len(self.balls) > 0:
                        ball.jump(True)
                    elif input == "left" and len(self.balls) > 0:
                        ball.jump(False)
                    # elif input == "quit":
                    #     self.balls = []

            @socket.on('quit')
            def quit_game(msg):
                print("QUITTING")
                if genomes:
                    self.kill = True
                self.balls = []
                # raise Exception()
                # self.balls = []
                # self.ge = []
                # self.nets = []
                # self.quit = True

            if self.kill:
                print("attempting to extincit these")
                if ge:
                    ge[0].fitness = sys.maxsize
                return

            i = len(self.balls) - 1
            while i >= 0:

                ball = self.balls[i]

                ball.move(nets, ge , i, self)

                i -= 1

            # if display: self.draw_window(win)#,  testBox)
            self.emit_data("screen", socket)


            if len(self.balls) == 0:
                self.__init__(self.custom_config)

                return

        #self.menu(win)