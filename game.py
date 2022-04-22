#from grpc import xds_server_credentials
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


bboxes = []
font = pygame.font.SysFont('Comic Sans MS', 30)



class BBox:
    global bboxes
    def __init__(self, x, y, height =5, width = 20, passable = False):
        self.x = x
        self.y = y+2
        self.width = width
        self.height = height
        self.rect = pygame.Rect((self.x, self.y) , (self.width, self.height))
        self.mask = pygame.mask.Mask((self.width, self.height), True)
        bboxes.append(self)
        self.passable = passable


    def draw(self, win):
        pygame.draw.rect(win, (0, 255, 0) if not self.passable else (0, 0 , 255), self.rect)


class Rim:
    def __init__(self, x, y):
        #left of rim edge
        self.x = x 
        self.y = y
        leftRim =  BBox(self.x if self.x == 0 else self.x -15, self.y)
        rightRim = BBox((self.x + HOOP_SIZE + 5 if self.x == 0 else self.x+HOOP_SIZE -15), self.y)
        goal = BBox(leftRim.x + leftRim.width, self.y, height = 5, width = HOOP_SIZE - leftRim.width, passable = True)
        self.bboxes = [leftRim, rightRim, goal]


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
        self.score = 0

    def draw(self, win):
        text_surface = font.render('Score: '+ str(self.score), False, (255, 255, 255))
        self.hoop.draw(win)
        win.blit(BALL_IMG, (self.x, self.y))
        win.blit(text_surface, (WIN_WIDTH/2,0))

        


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
        
       # print(round(self.x_vel), ", " , round(self.y_vel))


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

    def collide(self, bbox):
       col_point = self.mask.overlap(bbox.mask, (bbox.x - self.x, bbox.y-self.y)) 
       if col_point != None:
            
           # print("collision with bbox at ", bbox.x ,bbox.y)
            dx = self.x_vel
            dy =  self.y_vel * self.time + (self.y_acc) * (self.time ** 2)

            if not bbox.passable:

                if abs(dy) > abs(dx):
                    if dy > 0: 
                        self.y = bbox.y - BALL_SIZE
                        self.y_vel *= .65
                        self.x_vel *= 0.5
                        self.time = 0
                    elif dy < 0:
                        self.y = bbox.y + bbox.height
                        self.y_vel = 0
                        self.time = 0
                elif dy != 0 and dx != 0: 
                    print("bruh")
                    self.x_vel = 0
                    self.y_vel = 0
            elif dy > 0:
                self.score += 1

            '''
            if col_point[1] > 10 and (col_point[0] <= 40 or col_point[0] >= 10): #or self.y+BALL_SIZE > WIN_HEIGHT:
                #print("detedcetd")
                self.y = bbox.y - BALL_SIZE
                self.y_vel *= .65
                self.x_vel *= 0.5
                self.time = 0
            elif ((col_point[0] > 40 or col_point[0] < 10) and (col_point[1] >=10 and col_point[1]<=30)):
                self.x_vel = 0
                self.y_vel = 0
            

            elif col_point[1] <= 10: 
                self.y = bbox.y + bbox.height
                self.y_vel = 2
                self.time = 2

                '''

           



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


    




def draw_window(win, balls, testBox = None):
    win.blit(BG_IMG, (0,0))
    
    for ball in balls:
        ball.draw(win)
        #if hoop != None: ball.hoop.draw(win)

    

    # text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    # win.blit(text, (WIN_WIDTH-10 -text.get_width(), 10))
    if testBox != None: testBox.draw(win)    
    pygame.display.update()



def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    time = pygame.time.Clock()
    balls = [Ball()]
    ground = BBox(0, WIN_HEIGHT-20, 500, WIN_WIDTH)
    #testBox = BBox(300, 300, 20 ,20)
    #bboxes = [ground , hoop.rim.bboxes[0], hoop.rim.bboxes[1], testBox]


    while run:
        global bboxes
        for bbox in bboxes:
            print( "bbox at " , bbox.x ,", " ,bbox.y , end = " ")

        print()
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
                    bboxes = []
                    main()
 
                if event.key == pygame.K_d:
                        #print("jump right")
                        balls[0].jump(True)
                if event.key == pygame.K_a:
                        #print("jump left")
                        balls[0].jump(False)

        for ball in balls:
                        
            ball.move(bboxes)


        

        draw_window(win,balls)#,  testBox)


main()