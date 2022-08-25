from lib2to3.pytree import generate_matches
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



GEN = 0

class Game:
    config_path = "./config-feedforward.txt"


    def __init__(self):
        self.balls = []
        self.images = []
        self.show_display_options = False
    
    def replay_genome(self,  socket, ticks = 250, genome_path="winner.pkl"):
        # Load requried NEAT config
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

        # Unpickle saved winner
        with open(genome_path, "rb") as f:
            genome = pickle.load(f)

        # Convert loaded genome into required data structure
        genomes = [(1, genome)]

        # Call game with only the loaded genome
        self.main(genomes, config, ticks,socket, display = True, quit = True)
    

    def show_train(self):
        self.train_AI(True)

    def show_main(self, genomes, config):
        self.main(genomes,config,display= True)


    def train_AI(self, socket, display = False):
        config_path = "./config-feedforward.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
            neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
        

        p = neat.Population(config)


        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(self.main, 1000) if not display else p.run(self.show_main, 1000)

        if False:
            with open("winner.pkl", "wb") as f:
                pickle.dump(winner, f)
                f.close()


    # def draw_window(self, win, testBox = None, sp = False):
    #     self.game_bg_image.draw(win)

    #     for ball in self.balls:
    #         ball.draw(win)

    #     if testBox != None: testBox.draw(win)    
    #     pygame.display.update()

    def play_solo(self, socket):
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        time = pygame.time.Clock()
        
        ball = Ball(self)

        run = True
        images = []
        while run:
            global bboxes


            time.tick(250)

      
            def make_move(input):
                if input == "right":
                    self.balls[0].jump(True)
                elif input == "left":
                    self.balls[0].jump(False)
                elif input == "quit":
                    run = False
                    pygame.quit()
                    quit()

            socket.on('input', make_move)
                
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         run = False
            #         pygame.quit()
            #         quit()

            #     if event.type == pygame.KEYDOWN:
            #         if event.key == pygame.K_r:
            #             print("restarting")
            #             self.__init__()

            #         if event.key == pygame.K_d:
            #                 self.balls[0].jump(True)
            #         if event.key == pygame.K_a:
            #                 self.balls[0].jump(False)

           
        
            ball.move(None, None , -1, self)

            images_clone = []
            for image in images:
                images_clone.appen(image.to_list())

            
            socket.emit("screen",json.dumps(images))


            if len(self.balls) == 0:
                self.__init__()



    def main(self, genomes, config, ticks = 250, display = False, quit = False):
        nets = []
        ge = []

        for genome_id , g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            Ball(self)
            g.fitness = 0
            ge.append(g)

        if display:
            win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
            time = pygame.time.Clock()
            
        run = True
        while run:
            global bboxes
            if display: 
                time.tick(ticks)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                        quit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r and display:
                            print("restarting")
                            self.__init__()

            i = len(self.balls) - 1
            while i >= 0:

                ball = self.balls[i]

                ball.move(nets, ge , i, self)

                i -= 1

            if display: self.draw_window(win)#,  testBox)
            

            if len(self.balls) == 0:
                if quit:self.__init__()
                else:
                    return

        #self.menu(win)