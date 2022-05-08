#from grpc import xds_server_credentials
# from inspect import GEN_CLOSED
# from ipaddress import _IPAddressBase
import pygame
import time
import os
import random
pygame.font.init()
import neat
import pickle
from objects import Ball
from Image import Image, Button
from Game import Game


# WIN_WIDTH = 800
# WIN_HEIGHT = 500

# MENU_WIDTH = 750
# MENU_HEIGHT = 600

# BG_IMG = pygame.transform.scale( pygame.image.load(os.path.join("assets", "bg.jpg")), (WIN_WIDTH, WIN_HEIGHT))

# BALL_SIZE = 50
# BALL_IMG = pygame.transform.scale(
#     pygame.image.load(os.path.join("assets", "ball.png")), (BALL_SIZE, BALL_SIZE))

# BRAIN_BALL_IMG =  pygame.transform.scale(
#     pygame.image.load(os.path.join("assets", "bball_brain.png")), (BALL_SIZE, BALL_SIZE))

# BEST_BALL_IMG =  pygame.transform.scale(
#     pygame.image.load(os.path.join("assets", "winner_ball.png")), (BALL_SIZE,  BALL_SIZE))

# STAT_FONT = pygame.font.SysFont("comicsans", 50)



# MENU_BG = pygame.transform.scale(
 #   pygame.image.load(os.path.join("assets", "menu_bg.png")), (MENU_WIDTH, MENU_HEIGHT))




if __name__ == "__main__":
    game = Game()
    win = None
    game.menu(win)


