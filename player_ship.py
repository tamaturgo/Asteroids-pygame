from constants import *

import random
import math
import pygame

gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))


# Class player
class PlayerShip:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.h_speed = 0
        self.v_speed = 0
        self.dir = -90
        self.rt_speed = 0
        self.thrust = False

    def update_player(self):
        # Move player
        speed = math.sqrt(self.h_speed ** 2 + self.v_speed ** 2)
        if self.thrust:
            if speed + FD_FRIC < PLAYER_MAX_SPEED:
                self.h_speed += FD_FRIC * math.cos(self.dir * math.pi / 180)
                self.v_speed += FD_FRIC * math.sin(self.dir * math.pi / 180)
            else:
                self.h_speed = PLAYER_MAX_SPEED * math.cos(self.dir * math.pi / 180)
                self.v_speed = PLAYER_MAX_SPEED * math.sin(self.dir * math.pi / 180)
        else:
            if speed - BD_FRIC > 0:
                change_in_h_speed = (BD_FRIC * math.cos(self.v_speed / self.h_speed))
                change_in_v_speed = (BD_FRIC * math.sin(self.v_speed / self.h_speed))
                if self.h_speed != 0:
                    if change_in_h_speed / abs(change_in_h_speed) == self.h_speed / abs(self.h_speed):
                        self.h_speed -= change_in_h_speed
                    else:
                        self.h_speed += change_in_h_speed
                if self.v_speed != 0:
                    if change_in_v_speed / abs(change_in_v_speed) == self.v_speed / abs(self.v_speed):
                        self.v_speed -= change_in_v_speed
                    else:
                        self.v_speed += change_in_v_speed
            else:
                self.h_speed = 0
                self.v_speed = 0
        self.x += self.h_speed
        self.y += self.v_speed

        # Check for wrapping
        if self.x > WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIDTH
        elif self.y > HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = HEIGHT

        # Rotate player
        self.dir += self.rt_speed

    def draw_player(self):
        a = math.radians(self.dir)
        x = self.x
        y = self.y
        s = PLAYER_SIZE
        t = self.thrust
        # Draw player
        pygame.draw.line(gameDisplay, WHITE,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) + a),
                          y - (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) + a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(gameDisplay, WHITE,
                         (x - (s * math.sqrt(130) / 12) * math.cos(math.atan(7 / 9) - a),
                          y + (s * math.sqrt(130) / 12) * math.sin(math.atan(7 / 9) - a)),
                         (x + s * math.cos(a), y + s * math.sin(a)))

        pygame.draw.line(gameDisplay, WHITE,
                         (x - (s * math.sqrt(2) / 2) * math.cos(a + math.pi / 4),
                          y - (s * math.sqrt(2) / 2) * math.sin(a + math.pi / 4)),
                         (x - (s * math.sqrt(2) / 2) * math.cos(-a + math.pi / 4),
                          y + (s * math.sqrt(2) / 2) * math.sin(-a + math.pi / 4)))
        if t:
            pygame.draw.line(gameDisplay, WHITE,
                             (x - s * math.cos(a),
                              y - s * math.sin(a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(a + math.pi / 6),
                              y - (s * math.sqrt(5) / 4) * math.sin(a + math.pi / 6)))
            pygame.draw.line(gameDisplay, WHITE,
                             (x - s * math.cos(-a),
                              y + s * math.sin(-a)),
                             (x - (s * math.sqrt(5) / 4) * math.cos(-a + math.pi / 6),
                              y + (s * math.sqrt(5) / 4) * math.sin(-a + math.pi / 6)))

    def kill_player(self):
        # Reset the player
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.thrust = False
        self.dir = -90
        self.h_speed = 0
        self.v_speed = 0


# Create class for shattered ship
class DeadPlayerShip:
    def __init__(self, x, y, z):
        self.angle = random.randrange(0, 360) * math.pi / 180
        self.dir = random.randrange(0, 360) * math.pi / 180
        self.rt_speed = random.uniform(-0.25, 0.25)
        self.x = x
        self.y = y
        self.z = z
        self.speed = random.randint(2, 8)

    def update_dead_player(self):
        pygame.draw.line(gameDisplay, WHITE,
                         (self.x + self.z * math.cos(self.angle) / 2,
                          self.y + self.z * math.sin(self.angle) / 2),
                         (self.x - self.z * math.cos(self.angle) / 2,
                          self.y - self.z * math.sin(self.angle) / 2))
        self.angle += self.rt_speed
        self.x += self.speed * math.cos(self.dir)
        self.y += self.speed * math.sin(self.dir)
