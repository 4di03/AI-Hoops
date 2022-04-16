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
    def __init__(self, height):
        self.y = WIN_HEIGHT - height

  



class Ball:

    def __init__(self):
        self.x = (WIN_WIDTH/2) - BALL_SIZE
        self.y = (WIN_HEIGHT/2) - BALL_SIZE
        self.x_vel = 0
        self.y_vel = 0
        self.y_acc = 0.1
        self.hoop = Hoop()
        self.time = 0

    def draw(self, win):
        win.blit(BALL_IMG, (self.x, self.y))


    def jump(self, right):

        if right:
            self.x_vel = 2
        else:
            self.x_vel = -2


        self.y_vel = -1.3
        self.time = 0

    def move(self, base):
        self.collide(base)

        self.time += .25

        self.x += self.x_vel
        self.y += self.y_vel * self.time + (self.y_acc) * (self.time ** 2)

    def collide(self, base):
        if self.y + BALL_SIZE > base.y:
            self.y = base.y - BALL_SIZE
            self.y_vel *= .65
            self.x_vel *= 0.5
            self.time = 0


class Hoop:

    def __init__(self):
        self.x = random.randint(0,1) * (WIN_WIDTH - HOOP_SIZE)
        self.y = random.randint(0, WIN_HEIGHT*.75)
        self.img = HOOP_IMG.copy()
        self.img =  self.img if self.x == 0 else pygame.transform.flip(self.img, True, False)

    def draw(self, win):

        win.blit(self.img, (self.x, self.y))



def draw_window(win, balls, hoop):
    win.blit(BG_IMG, (0,0))
    
    for ball in balls:
        ball.draw(win)
        ball.hoop.draw(win)

    

    # text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    # win.blit(text, (WIN_WIDTH-10 -text.get_width(), 10))
    
    pygame.display.update()



def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    time = pygame.time.Clock()
    balls = [Ball()]
    hoop = Hoop()
    ground = BBox(20)



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
                        
            ball.move(ground)



        draw_window(win,balls, hoop)


main()