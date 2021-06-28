from constants import *

import math
import pygame

gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))


# Create class bullet
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.dir = direction
        self.life = 30

    def update_bullet(self):
        # Moving
        self.x += BULLET_SPEED * math.cos(self.dir * math.pi / 180)
        self.y += BULLET_SPEED * math.sin(self.dir * math.pi / 180)

        # Drawing
        pygame.draw.circle(gameDisplay, WHITE, (int(self.x), int(self.y)), 3)
        if self.x > WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIDTH
        elif self.y > HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = HEIGHT
        self.life -= 1
