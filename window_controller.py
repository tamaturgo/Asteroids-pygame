# Import modules
import pygame
import math
import random

from constants import *

from asteroids import Asteroid
from player_ship import PlayerShip, DeadPlayerShip
from bullets import Bullet
from alien_ship import AlienShip

pygame.init()

gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
timer = pygame.time.Clock()

snd_bangL = pygame.mixer.Sound("Sounds/bangLarge.wav")
snd_fire = pygame.mixer.Sound("Sounds/fire.wav")
snd_bangM = pygame.mixer.Sound("Sounds/bangMedium.wav")
snd_bangS = pygame.mixer.Sound("Sounds/bangSmall.wav")
snd_extra = pygame.mixer.Sound("Sounds/extra.wav")
snd_saucerB = pygame.mixer.Sound("Sounds/saucerBig.wav")
snd_saucerS = pygame.mixer.Sound("Sounds/saucerSmall.wav")


def draw_text(msg, color, x, y, s, center=True):
    screen_text = pygame.font.Font("Fonts/PressStart2P.ttf", s).render(msg, True, color)
    if center:
        rect = screen_text.get_rect()
        rect.center = (x, y)
    else:
        rect = (x, y)
    gameDisplay.blit(screen_text, rect)


# Check Collisions
def is_colliding(x, y, x_to, y_to, size):
    if x_to - size < x < x_to + size and y_to - size < y < y_to + size:
        return True
    return False


def game_loop(starting_state):

    # Init variables from window
    game_state = starting_state
    player_state = "Alive"
    player_blink = 0
    player_pieces = []
    player_dying_delay = 0
    player_invisible_dur = 0
    hyperspace = 0
    next_level_delay = 0
    bullet_capacity = 4
    bullets = []
    asteroids = []
    stage = 3
    score = 0
    live = 2
    one_up_multiplier = 1
    play_one_up_sfx = 0
    intensity = 0
    player = PlayerShip(WIDTH / 2, HEIGHT / 2)
    alien_ship = AlienShip()

    while game_state != "Exit":

        # Game menu
        while game_state == "Menu":
            gameDisplay.fill(BLACK)
            draw_text("ASTEROIDS", WHITE, WIDTH / 2, HEIGHT / 2, 50)
            draw_text("Press any key to START", WHITE, WIDTH / 2, HEIGHT / 2 + 100, 25)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = "Exit"
                if event.type == pygame.KEYDOWN:
                    game_state = "Playing"
            pygame.display.update()
            timer.tick(5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "Exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.thrust = True
                if event.key == pygame.K_LEFT:
                    player.rt_speed = -PLAYER_MAX_RTSPD
                if event.key == pygame.K_RIGHT:
                    player.rt_speed = PLAYER_MAX_RTSPD
                if event.key == pygame.K_SPACE and player_dying_delay == 0 and len(bullets) < bullet_capacity:
                    bullets.append(Bullet(player.x, player.y, player.dir))
                    pygame.mixer.Sound.play(snd_fire)
                if game_state == "Game Over":
                    if event.key == pygame.K_r:
                        game_state = "Exit"
                        game_loop("Playing")
                """if event.key == pygame.K_LSHIFT:
                    hyperspace = 30"""
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player.thrust = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.rt_speed = 0

        player.update_player()

        # Checking player invincible time
        if player_invisible_dur != 0:
            player_invisible_dur -= 1
        elif hyperspace == 0:
            player_state = "Alive"

        # Reset display
        gameDisplay.fill(BLACK)

        """"# Hyperspace
        if hyperspace != 0:
            player_state = "Died"
            hyperspace -= 1
            if hyperspace == 1:
                player.x = random.randrange(0, WIDTH)
                player.y = random.randrange(0, HEIGHT)"""

        # Check for collision with the asteroid
        for a in asteroids:
            a.update_asteroid()
            if player_state != "Died":
                if is_colliding(player.x, player.y, a.x, a.y, a.size):

                    # Create ship fragments
                    player_pieces.append(
                        DeadPlayerShip(player.x, player.y, 5 * PLAYER_SIZE / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(
                        DeadPlayerShip(player.x, player.y, 5 * PLAYER_SIZE / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(DeadPlayerShip(player.x, player.y, PLAYER_SIZE))

                    # Kill player
                    player_state = "Died"
                    player_dying_delay = 30
                    player_invisible_dur = 120
                    player.kill_player()

                    if live != 0:
                        live -= 1
                    else:
                        game_state = "Game Over"

                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        score += 20
                        pygame.mixer.Sound.play(snd_bangL)

                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        score += 50
                        pygame.mixer.Sound.play(snd_bangM)

                    else:
                        score += 100
                        pygame.mixer.Sound.play(snd_bangS)
                    asteroids.remove(a)

        # Update ship fragments
        for f in player_pieces:
            f.update_dead_player()
            if f.x > WIDTH or f.x < 0 or f.y > HEIGHT or f.y < 0:
                player_pieces.remove(f)

        # Check for end of stage
        if len(asteroids) == 0 and alien_ship.state == "Dead":
            if next_level_delay < 30:
                next_level_delay += 1
            else:
                stage += 1
                intensity = 0
                # Spawn asteroid away of center
                for i in range(stage):
                    x_to = WIDTH / 2
                    y_to = HEIGHT / 2
                    while x_to - WIDTH / 2 < WIDTH / 4 and y_to - HEIGHT / 2 < HEIGHT / 4:
                        x_to = random.randrange(0, WIDTH)
                        y_to = random.randrange(0, HEIGHT)
                    asteroids.append(Asteroid(x_to, y_to, "Large"))
                next_level_delay = 0

        # Update intensity
        if intensity < stage * 450:
            intensity += 1

        # Alien
        if alien_ship.state == "Dead":
            if random.randint(0, 6000) <= (intensity * 2) / (stage * 9) and next_level_delay == 0:
                alien_ship.create_alien_ship()
                if score >= 40000:
                    alien_ship.type = "Small"
        else:

            # Set alien target direction
            acc = ALIEN_ACCURACY * 4 / stage
            alien_ship.b_dir = math.degrees(
                math.atan2(-alien_ship.y + player.y, -alien_ship.x + player.x)
                + math.radians(random.uniform(acc, -acc)))

            alien_ship.update_alien_ship()
            alien_ship.draw_alien_ship()

            # Check for collision with the asteroid
            for a in asteroids:
                if is_colliding(alien_ship.x, alien_ship.y, a.x, a.y, a.size + alien_ship.size):
                    alien_ship.state = "Dead"

                    # Split asteroid
                    if a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        pygame.mixer.Sound.play(snd_bangM)

                    elif a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        pygame.mixer.Sound.play(snd_bangL)

                    else:
                        pygame.mixer.Sound.play(snd_bangS)
                    asteroids.remove(a)

            # Check for collision with the bullet
            for b in bullets:
                if is_colliding(b.x, b.y, alien_ship.x, alien_ship.y, alien_ship.size):

                    # Add points
                    if alien_ship.type == "Large":
                        score += 200
                    else:
                        score += 1000
                    alien_ship.state = "Dead"

                    pygame.mixer.Sound.play(snd_bangL)

                    bullets.remove(b)

            # Check collision with the player
            if is_colliding(alien_ship.x, alien_ship.y, player.x, player.y, alien_ship.size):
                if player_state != "Died":

                    # Create ship fragments
                    player_pieces.append(
                        DeadPlayerShip(player.x, player.y, 5 * PLAYER_SIZE / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(
                        DeadPlayerShip(player.x, player.y, 5 * PLAYER_SIZE / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(DeadPlayerShip(player.x, player.y, PLAYER_SIZE))

                    # Kill player
                    player_state = "Died"
                    player_dying_delay = 30
                    player_invisible_dur = 120
                    player.kill_player()

                    if live != 0:
                        live -= 1
                    else:
                        game_state = "Game Over"

                    pygame.mixer.Sound.play(snd_bangL)

            # Alien bullets
            for b in alien_ship.bullets:
                # Update bullets
                b.update_bullet()

                # Check for collision with the asteroids
                for a in asteroids:
                    if is_colliding(b.x, b.y, a.x, a.y, a.size):

                        # Split asteroid
                        if a.t == "Large":
                            asteroids.append(Asteroid(a.x, a.y, "Normal"))
                            asteroids.append(Asteroid(a.x, a.y, "Normal"))
                            pygame.mixer.Sound.play(snd_bangL)

                        elif a.t == "Normal":
                            asteroids.append(Asteroid(a.x, a.y, "Small"))
                            asteroids.append(Asteroid(a.x, a.y, "Small"))
                            pygame.mixer.Sound.play(snd_bangL)

                        else:
                            pygame.mixer.Sound.play(snd_bangL)

                        # Remove asteroid and bullet
                        asteroids.remove(a)
                        alien_ship.bullets.remove(b)

                        break

                # Check for collision with the player
                if is_colliding(player.x, player.y, b.x, b.y, 5):
                    if player_state != "Died":
                        # Create ship fragments
                        player_pieces.append(
                            DeadPlayerShip(player.x, player.y, 5 * PLAYER_SIZE / (2 * math.cos(math.atan(1 / 3)))))
                        player_pieces.append(
                            DeadPlayerShip(player.x, player.y, 5 * PLAYER_SIZE / (2 * math.cos(math.atan(1 / 3)))))
                        player_pieces.append(DeadPlayerShip(player.x, player.y, PLAYER_SIZE))

                        # Kill player
                        player_state = "Died"
                        player_dying_delay = 30
                        player_invisible_dur = 120
                        player.kill_player()

                        if live != 0:
                            live -= 1
                        else:
                            game_state = "Game Over"

                        pygame.mixer.Sound.play(snd_bangL)

                        alien_ship.bullets.remove(b)

                if b.life <= 0:
                    try:
                        alien_ship.bullets.remove(b)
                    except ValueError:
                        continue

        # Bullets
        for b in bullets:
            # Update bullets
            b.update_bullet()

            # Check for bullets collide with the asteroid
            for a in asteroids:
                if a.x - a.size < b.x < a.x + a.size and a.y - a.size < b.y < a.y + a.size:
                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        score += 20
                        pygame.mixer.Sound.play(snd_bangL)

                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        score += 50
                        pygame.mixer.Sound.play(snd_bangM)

                    else:
                        score += 100
                        pygame.mixer.Sound.play(snd_bangS)
                    asteroids.remove(a)
                    bullets.remove(b)

                    break

            # Destroying bullets
            if b.life <= 0:
                try:
                    bullets.remove(b)
                except ValueError:
                    continue

        # Extra live
        if score > one_up_multiplier * 10000:
            one_up_multiplier += 1
            live += 1
            play_one_up_sfx = 60
        if play_one_up_sfx > 0:
            play_one_up_sfx -= 1
            pygame.mixer.Sound.play(snd_extra, 60)

        # Draw player
        if game_state != "Game Over":
            if player_state == "Died":
                if hyperspace == 0:
                    if player_dying_delay == 0:
                        if player_blink < 5:
                            if player_blink == 0:
                                player_blink = 10
                            else:
                                player.draw_player()
                        player_blink -= 1
                    else:
                        player_dying_delay -= 1
            else:
                player.draw_player()
        else:
            draw_text("Game Over", WHITE, WIDTH / 2, HEIGHT / 2, 50)
            draw_text("Press \"R\" to restart!", WHITE, WIDTH / 2, HEIGHT / 2 + 100, 25)
            live = -1

        # Draw score
        draw_text(str(score), WHITE, 60, 20, 40, False)

        # Draw Lives
        for i in range(live + 1):
            PlayerShip(75 + i * 25, 75).draw_player()

        # Update screen
        pygame.display.update()

        # Tick fps
        timer.tick(30)


# Start game
game_loop("Menu")

# End game
pygame.quit()
quit()
