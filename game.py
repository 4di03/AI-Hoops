from grpc import xds_server_credentials
import pygame
import time
import os
import random
pygame.font.init()


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



class BBox:
    def __init__(self, x, y, height =20, width = 20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect((self.x, self.y) , (self.width, self.height))
        self.mask = pygame.mask.Mask((self.width, self.height), True)


    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), self.rect)


class Rim:
    def __init__(self, x, y):
        #left of rim edge
        self.x = x
        self.y = y + 30
        self.bboxes = [BBox(x, y), BBox(x+ HOOP_SIZE-30, y)]


    def draw(self, win):
       for b in self.bboxes:
           b.draw(win)

class Ball:

    def __init__(self):
        self.x = (WIN_WIDTH/2) - BALL_SIZE
        self.y = (WIN_HEIGHT/2) - BALL_SIZE
        self.x_vel = 0
        self.y_vel = 0
        self.y_acc = 0.1
        self.hoop = Hoop()
        self.time = 0
        self.mask = pygame.mask.from_surface(BALL_IMG)

    def draw(self, win):
        win.blit(BALL_IMG, (self.x, self.y))


    def jump(self, right):

        if right:
            self.x_vel = 2
        else:
            self.x_vel = -2


        self.y_vel = -1.3
        self.time = 0

    def move(self, bboxes):
        for bbox in bboxes:
            self.collide(bbox)

        self.time += .25


        self.x += self.x_vel

        if (self.x <= -BALL_SIZE):
            self.x = WIN_WIDTH - BALL_SIZE
        elif(self.x > WIN_WIDTH):
            self.x = 0

        self.y += self.y_vel * self.time + (self.y_acc) * (self.time ** 2)

        if self.y < -200:
            self.y = -200

    def collide(self, bbox):
        

       # if self.y + BALL_SIZE > bbox.y:
       if self.mask.overlap(bbox.mask, (bbox.x - self.x, bbox.y-self.y)) != None:
            self.y = bbox.y - BALL_SIZE
            self.y_vel *= .65
            self.x_vel *= 0.5
            self.time = 0


class Hoop:

    def __init__(self):
        self.x = random.randint(0,1) * (WIN_WIDTH - HOOP_SIZE)
        self.y = random.randint(0, WIN_HEIGHT*.75)
        self.img = HOOP_IMG.copy()
        self.img =  self.img if self.x == 0 else pygame.transform.flip(self.img, True, False)
        print(self.x, self.y)
        self.rim = Rim(self.x, self.y)
        print(self.rim.x, self.rim.y)

    def draw(self, win):

        win.blit(self.img, (self.x, self.y))
        self.rim.draw(win)


    




def draw_window(win, balls, hoop, testBox):
    win.blit(BG_IMG, (0,0))
    
    for ball in balls:
        ball.draw(win)
        ball.hoop.draw(win)

    

    # text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    # win.blit(text, (WIN_WIDTH-10 -text.get_width(), 10))
    testBox.draw(win)    
    pygame.display.update()



def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    time = pygame.time.Clock()
    balls = [Ball()]
    hoop = Hoop()
    ground = BBox(0, WIN_HEIGHT-20, 20, WIN_WIDTH)
    testBox = BBox(300, 300, 60 ,60)
    bboxes = [ground , hoop.rim.bboxes[0], hoop.rim.bboxes[1], BBox(300, 300, 60, 60)]


    while run:
        time.tick(250)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    print("restarting")
                    pygame.quit()
                    main()

                if event.key == pygame.K_d:
                        print("jump right")
                        balls[0].jump(True)
                if event.key == pygame.K_a:
                        print("jump left")
                        balls[0].jump(False)

        for ball in balls:
                        
            ball.move(bboxes)


        

        draw_window(win,balls, hoop, testBox)


main()