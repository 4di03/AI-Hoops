import pygame
import time
import os
import random
pygame.font.init()
import neat
import pickle
from objects import Ball
from Image import Image, Button
from objects import WIN_HEIGHT, WIN_WIDTH, STAT_FONT, MENU_WIDTH, MENU_HEIGHT, BALL_IMG, BALL_SIZE, BRAIN_BALL_IMG, BEST_BALL_IMG, MENU_BG, BG_IMG

GEN = 0
font = pygame.font.SysFont('Comic Sans MS', 10)

class Game:
    config_path = "./config-feedforward.txt"


    menu_bg_image = Image(MENU_BG, 0, 0 , MENU_WIDTH, MENU_HEIGHT)
    game_bg_image = Image(BG_IMG, 0, 0 , WIN_WIDTH, WIN_HEIGHT)

    balls = []
    
    def replay_genome(self,  ticks = 250, genome_path="winner.pkl"):
        # Load requried NEAT config
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, self.config_path)

        # Unpickle saved winner
        with open(genome_path, "rb") as f:
            genome = pickle.load(f)

        # Convert loaded genome into required data structure
        genomes = [(1, genome)]

        # Call game with only the loaded genome
        self.main(genomes, config, ticks, display = True)



    def train_AI(self):
        config_path = "./config-feedforward.txt"
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
            neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
        

        p = neat.Population(config)


        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(self.main, 1000)

        if False:
            with open("winner.pkl", "wb") as f:
                pickle.dump(winner, f)
                f.close()

    def menu(self, win):
        self.balls = []
        win = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
        time = pygame.time.Clock()

        single_player_button = Button(BALL_IMG, 100, 50, BALL_SIZE, BALL_SIZE, self.play_solo)

        train_ai_button = Button(BRAIN_BALL_IMG, 350, 50, BALL_SIZE, BALL_SIZE, self.train_AI)

        play_winner_button = Button(BEST_BALL_IMG, 600, 20, BALL_SIZE + 10, BALL_SIZE + 30, self.replay_genome)


        buttons = [single_player_button, train_ai_button, play_winner_button]
        while True:
            self.menu_bg_image.draw(win)
            time.tick(250)

            for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                        quit()

                    if event.type == pygame.MOUSEBUTTONUP:
                        pos = pygame.mouse.get_pos()
                 
                        print(pos)
                        for button in buttons:
                            if button.clicked(pos[0], pos[1]):
                                button.execute()



            sp_text = font.render('Play Solo:'+ str(self.score), False, (255, 255, 255))


            
            #draw buttons 
            single_player_button.draw(win)
            train_ai_button.draw(win)
            play_winner_button.draw(win)

            pygame.display.update()

    def draw_window(self, win, testBox = None, sp = False):
        self.game_bg_image.draw(win)

        for ball in self.balls:
            ball.draw(win)

        if testBox != None: testBox.draw(win)    
        pygame.display.update()

    def play_solo(self):
        win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        time = pygame.time.Clock()
        
        ball = Ball(self)

        run = True
        while run:
            global bboxes


            time.tick(250)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        print("restarting")
                        self.menu(win)

                    if event.key == pygame.K_d:
                            self.balls[0].jump(True)
                    if event.key == pygame.K_a:
                            self.balls[0].jump(False)

           
        
            ball.move(None, None , -1, self)

            self.draw_window(win)#,  testBox)
            if len(self.balls) == 0:
                self.menu(win)



    def main(self, genomes, config, ticks = 2500, display = False):
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
                        if event.key == pygame.K_r:
                            print("restarting")
                            self.menu(win)

            i = len(self.balls) - 1
            while i >= 0:

                ball = self.balls[i]

                ball.move(nets, ge , i, self)

                i -= 1

            if display: self.draw_window(win)#,  testBox)
            

            if len(self.balls) == 0:
                self.menu(win)

        self.menu(win)