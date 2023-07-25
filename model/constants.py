import pygame

import math


WIN_WIDTH = 1920 # 800
WIN_HEIGHT = 1080 # 500
BG_IMG = pygame.transform.scale( pygame.image.load("static/assets/bg.jpg"), (WIN_WIDTH, WIN_HEIGHT))

BALL_SIZE = 100
BALL_IMG = pygame.transform.scale(
    pygame.image.load("static/assets/ball.png"), (BALL_SIZE, BALL_SIZE))

BRAIN_BALL_IMG =  pygame.transform.scale(
    pygame.image.load("static/assets/bball_brain.png"), (BALL_SIZE, BALL_SIZE))

BEST_BALL_IMG =  pygame.transform.scale(
    pygame.image.load("static/assets/winner_ball.png"), (BALL_SIZE, BALL_SIZE))

HOOP_SIZE= 200
HOOP_IMG = pygame.transform.scale(
    pygame.image.load("static/assets/hoop2.png"), (HOOP_SIZE, HOOP_SIZE))


STAT_FONT = pygame.font.SysFont("comicsans", 50)


font = pygame.font.SysFont('Comic Sans MS', 10)

AI_MOVE_INTERVAL = 50 # interval between AI moves in ticks

GEN = 0
MIN_VEL = 0.1
BBOX_WIDTH = 10
BBOX_HEIGHT = 10

PRINT_GRAVITY_TIME = False



CTPS = 500

HORIZONTAL_VEL = 4 * 250/CTPS # speed per tick
ACC = 0.02 * math.sqrt(250/CTPS) # acc per tick
Y_VEL = -3 * math.sqrt(HORIZONTAL_VEL)/1.6 # speed per tick