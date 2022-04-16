import pygame
import time
import os
import random
pygame.font.init()


WIN_WIDTH = 800
WIN_HEIGHT = 480

BG_IMG = pygame.image.load(os.path.join("assets", "bg.jpg"))

STAT_FONT = pygame.font.SysFont("comicsans", 50)






def draw_window(win):
    win.blit(BG_IMG, (0,-20))
    

    # text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    # win.blit(text, (WIN_WIDTH-10 -text.get_width(), 10))
    
    pygame.display.update()



def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    while run:
        draw_window(win)

main()