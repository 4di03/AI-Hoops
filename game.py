#from grpc import xds_server_credentials
from inspect import GEN_CLOSED
from ipaddress import _IPAddressBase
import pygame
import time
import os
import random
pygame.font.init()
import neat
import pickle

balls = []

WIN_WIDTH = 800
WIN_HEIGHT = 500

BG_IMG = pygame.transform.scale( pygame.image.load(os.path.join("assets", "bg.jpg")), (WIN_WIDTH, WIN_HEIGHT))

BALL_SIZE = 50
BALL_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "ball.png")), (BALL_SIZE, BALL_SIZE))


HOOP_SIZE= 100
HOOP_IMG = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "hoop2.png")), (HOOP_SIZE, HOOP_SIZE))


STAT_FONT = pygame.font.SysFont("comicsans", 50)

ALLOWED_TIME = 1200

font = pygame.font.SysFont('Comic Sans MS', 10)

GEN = 0

BBOX_WIDTH = 10
BBOX_HEIGHT = 10

class BBox:
    def __init__(self, x, y, height = BBOX_HEIGHT, width = BBOX_WIDTH, passable = False):
        self.x = x
        self.y = y+2
        self.width = width
        self.height = height
        self.rect = pygame.Rect((self.x, self.y) , (self.width, self.height))
        self.mask = pygame.mask.Mask((self.width, self.height), True)
        self.passable = passable


    def draw(self, win):
        pygame.draw.rect(win, (0, 255, 0) if not self.passable else (0, 0 , 255), self.rect)

ground = BBox(0, WIN_HEIGHT-20, 500, WIN_WIDTH)


class Rim:
    def __init__(self, x, y):
        #left of rim edge
        self.x = x 
        self.y = y
        leftRim =  BBox(self.x , self.y)
        rightRim = BBox((self.x + HOOP_SIZE) if self.x == 0 else self.x + HOOP_SIZE - BBOX_WIDTH, self.y)
        self.goal = BBox(leftRim.x + leftRim.width, self.y, height = 5, width = HOOP_SIZE - leftRim.width, passable = True)
        self.bboxes = [ self.goal, leftRim, rightRim]


    def draw(self, win):
         
        for b in self.bboxes:
          b.draw(win)


class Ball:
    global balls
    global ground
    def __init__(self):
        self.x = (WIN_WIDTH/2) - BALL_SIZE
        self.y = (WIN_HEIGHT/2) - BALL_SIZE
        self.x_vel = 0
        self.y_vel = 0
        self.y_acc = 0.1
        self.hoop = Hoop()
        self.time = 0
        self.mask = pygame.mask.from_surface(BALL_IMG)
        self.score = 0
        self.tick = ALLOWED_TIME
        balls.append(self)
        self.tick0 = 0

    def draw(self, win):
        hpBar = pygame.Rect((self.x, self.y -20) , (BALL_SIZE * (self.tick/ALLOWED_TIME), 15))

        text_surface = font.render('Score: '+ str(self.score), False, (255, 255, 255))
        text_surface2 = font.render('Hoop at: '+ str(self.hoop.x) + ", " +str(self.hoop.y), False, (255, 255, 255))

   

        self.hoop.draw(win)
        win.blit(BALL_IMG, (self.x, self.y))
        pygame.draw.rect(win,(0, 255, 0), hpBar)
        win.blit(text_surface, (self.x + BALL_SIZE/2 - 20, self.y+BALL_SIZE/2 - 10))

    def jump(self, right):

        if right:
            self.x_vel = 2
        else:
            self.x_vel = -2

        self.y_vel = -1.3
        self.time = 0

    def move(self, nets , ge ,i):
        self.tick0 += 1
        
        self.tick -= 1

        if self.tick <= 0:
     
            balls.pop(i)
            nets.pop(i)
            ge.pop(i)
            return
        for bbox in self.hoop.rim.bboxes:
            self.collide(bbox, ge, i)

        self.collide(ground,ge , i)

        self.time += .25


        self.x += self.x_vel

        if (self.x <= -BALL_SIZE):
            self.x = WIN_WIDTH - BALL_SIZE
        elif(self.x > WIN_WIDTH):
            self.x = 0

        dy =  self.y_vel * self.time + (self.y_acc) * (self.time ** 2)


        self.y += dy

        if self.y < -200:
            self.y = -200

        if self.tick0 % 50 == 0:

            output = nets[i].activate((self.hoop.x - self.x, self.hoop.y - self.y, 
                self.x_vel, dy, self.tick/ALLOWED_TIME, self.y+BALL_SIZE > self.hoop.y))

            x = output.index(max(output))

            if x == 0:
                self.jump(True)
            elif x == 1:
                self.jump(False)

    def collide(self, bbox, ge, i):
       col_point = self.mask.overlap(bbox.mask, (bbox.x - self.x, bbox.y-self.y)) 
       if col_point != None:
            
           # print("collision with bbox at ", bbox.x ,bbox.y)
            dx = self.x_vel
            dy =  self.y_vel * self.time + (self.y_acc) * (self.time ** 2)

            if not bbox.passable:
                
                if self.y < bbox.y:
                    self.y = bbox.y - BALL_SIZE
                    self.y_vel *= .65
                    self.x_vel *= 0.5
                elif self.y >= bbox.y + bbox.height * .8:
                    self.y = bbox.y + bbox.height
                    self.y_vel = 0
                else:
                    self.x_vel *= -1
                    self.y_vel *= -1
                    self.x += 10 * self.x_vel
                    self.y += 10 * self.y_vel    

                self.time = 0


            elif dy > 0:
                self.tick = ALLOWED_TIME
                self.y = bbox.y+bbox.height + 20
                self.score += 1
                ge[i].fitness += 100
                self.hoop = Hoop()


class Hoop:
    #global bboxes
    def __init__(self):
        self.x = random.randint(0,1) * (WIN_WIDTH - HOOP_SIZE)
        self.y = random.randint(0, WIN_HEIGHT*.75)
        self.img = HOOP_IMG.copy()
        self.img =  self.img if self.x == 0 else pygame.transform.flip(self.img, True, False)
        self.rim = Rim(self.x, self.y)

    def draw(self, win):

        win.blit(self.img, (self.x, self.y))
        self.rim.draw(win)



def draw_window(win, balls, testBox = None):
    win.blit(BG_IMG, (0,0))
    
    for ball in balls:
        ball.draw(win)
        #if hoop != None: ball.hoop.draw(win)

    

    text = STAT_FONT.render("Generation: " + str(GEN), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH/2 - text.get_width(), 10))
    if testBox != None: testBox.draw(win)    
    pygame.display.update()



def main(genomes, config, ticks = 250, display = False):
    global GEN
    global balls
    
    GEN += 1
  
    nets = []
    ge = []

    for genome_id , g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        Ball()
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

        i = len(balls) - 1
        while i >= 0:

            ball = balls[i]

            ball.move(nets, ge , i)

            i -= 1

        if display: draw_window(win,balls)#,  testBox)

        if len(balls) == 0:
            return




def replay_genome(config_path, ticks = 250, genome_path="winner.pkl"):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    main(genomes, config, ticks, display = True)

if __name__ == "__main__":

    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)


    p = neat.Population(config)


    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 1000)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()


