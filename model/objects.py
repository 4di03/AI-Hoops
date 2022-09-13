#from grpc import xds_server_credentials
# from inspect import GEN_CLOSED
# from ipaddress import _IPAddressBase
from operator import truediv
import pygame

import random
pygame.font.init()

from model.Image import Image, Button


WIN_WIDTH = 800
WIN_HEIGHT = 500



BG_IMG = pygame.transform.scale( pygame.image.load("static/assets/bg.jpg"), (WIN_WIDTH, WIN_HEIGHT))

BALL_SIZE = 50
BALL_IMG = pygame.transform.scale(
    pygame.image.load("static/assets/ball.png"), (BALL_SIZE, BALL_SIZE))

BRAIN_BALL_IMG =  pygame.transform.scale(
    pygame.image.load("static/assets/bball_brain.png"), (BALL_SIZE, BALL_SIZE))

BEST_BALL_IMG =  pygame.transform.scale(
    pygame.image.load("static/assets/winner_ball.png"), (BALL_SIZE, BALL_SIZE))

HOOP_SIZE= 100
HOOP_IMG = pygame.transform.scale(
    pygame.image.load("static/assets/hoop2.png"), (HOOP_SIZE, HOOP_SIZE))


STAT_FONT = pygame.font.SysFont("comicsans", 50)

ALLOWED_TIME = 400

font = pygame.font.SysFont('Comic Sans MS', 10)

GEN = 0

BBOX_WIDTH = 10
BBOX_HEIGHT = 10

HORIZONTAL_VEL = 3.5
ACC = 0.1

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
        self.drawable = False


    def draw(self, win):
        
        if self.drawable:
            for b in self.bboxes:
                b.draw(win)


class Ball:
    def __init__(self, game):
        self.x = (WIN_WIDTH/2) - BALL_SIZE
        self.y = (WIN_HEIGHT/2) - BALL_SIZE
        self.x_vel = 0
        self.y_vel = 0
        self.y_acc = ACC
        self.hoop = Hoop(game)
        self.time = 0
        self.mask = pygame.mask.from_surface(BALL_IMG)
        self.score = 0
        self.tick = ALLOWED_TIME
        game.balls.append(self)
        self.tick0 = 0
        self.img = Image(BALL_IMG, self.x, self.y, BALL_SIZE, BALL_SIZE, "static/assets/ball.png")
        game.images.append(self.img)
        self.game = game


    def draw(self, win):
        hpBar = pygame.Rect((self.x, self.y -20) , (BALL_SIZE * (self.tick/ALLOWED_TIME), 15))

        text_surface = font.render('Score: '+ str(self.score), False, (255, 255, 255))
        text_surface2 = font.render('Hoop at: '+ str(self.hoop.x) + ", " +str(self.hoop.y), False, (255, 255, 255))
        self.hoop.draw(win)
        self.img.draw(win)
        pygame.draw.rect(win,(0, 255, 0), hpBar)
        win.blit(text_surface, (self.x + BALL_SIZE/2 - 20, self.y+BALL_SIZE/2 - 10))

    def jump(self, right):

        if right:
            self.x_vel = HORIZONTAL_VEL
        else:
            self.x_vel = -HORIZONTAL_VEL

        self.y_vel = -1.4
        self.time = 0

    def move(self, nets , ge ,i,game):
        self.tick0 += 1
        
        self.tick -= 1

        if self.tick <= 0:
     
            game.balls.pop(i)

            if nets and ge:
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

        self.img.update(self.x, self.y)

        if self.y < -200:
            self.y = -200
        if nets and ge:
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
                if ge:
                    ge[i].fitness += 100
                self.hoop = Hoop(self.game)


    def get_data(self):

        data = {"images":[], "text": [], "rectangles":[]}

        data["images"].append(self.img.to_list())
        data["images"].append(self.hoop.img.to_list())
        data["text"].append([(self.x + BALL_SIZE/2 - 20, self.y+BALL_SIZE/2 - 10),"Score: " + str(self.score), (255,255,255),"12px Arial"])
        data["rectangles"].append([(self.x, self.y -20) , (BALL_SIZE * (self.tick/ALLOWED_TIME), 15), "green"])

        
        return data


class Hoop:
    #global bboxes
    def __init__(self, game):
        self.x = random.randint(0,1) * (WIN_WIDTH - HOOP_SIZE)
        self.y = random.randint(0, WIN_HEIGHT*.75)
        self.img_copy = HOOP_IMG.copy()    

        if self.x == 0:
            self.img= Image(self.img_copy, self.x, self.y, HOOP_SIZE, HOOP_SIZE,"static/assets/hoop2.png")
        else: 
            self.img = Image(pygame.transform.flip(self.img_copy, True, False), self.x, self.y, HOOP_SIZE, HOOP_SIZE,"static/assets/hoop2.png")
            self.img.reversed = True
        
        self.rim = Rim(self.x, self.y)
        game.images.append(self.img)

    def draw(self, win):

        self.img.draw(win)
        self.rim.draw(win)
