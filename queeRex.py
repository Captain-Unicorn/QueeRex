import pygame
import random
import math
import os
import sys

# high score file
app_storage_path = os.path.expanduser("~")
high_score_file_path = os.path.join(app_storage_path, "high_score.txt")

if not os.path.exists(high_score_file_path):
    with open(high_score_file_path, 'w') as f:
        for i in range(10):
            f.write("AAA 0\n")

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("QueeRex: the jumper of fuck bois")

BACKDROP = (134, 144, 244)
GROUND_COLOR = (100, 100, 100)

rex_img = pygame.image.load('rex.png')
rex_rect = rex_img.get_rect(topleft=(50, HEIGHT - 5))

trumpy_img = pygame.image.load('trumpy.png')
cloud_img = pygame.image.load('clouds.png')

SPEED = 6.5
JUMP_STRENGTH = -22
GRAVITY = .85
vertical_speed = 0
ground = HEIGHT - 50
CLOUD_SPEED = 2

score = 0
high_scores = []
running = True
in_jump = False
clock = pygame.time.Clock()
dashed_line_offset = 0
min_spawn_delay = 700
max_spawn_delay = 2000
spawn_timer = pygame.time.get_ticks() + random.randint(min_spawn_delay, max_spawn_delay)

class Trumpy:
    def __init__(self, rect):
        self.rect = rect
        self.passed = False

class Cloud:
    def __init__(self, rect):
        self.rect = rect

trumpys = [Trumpy(trumpy_img.get_rect(topleft=(WIDTH + 100, HEIGHT - 100)))]

# game over screen
def game_over_screen(score):
    global high_scores

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    initials = ["A", "A", "A"]
    index = 0
    font = pygame.font.Font(None, 36)
    score_color = (128, 0, 128)  # purple-ish
    lowest_high_score = high_scores[-1][1] if high_scores else 0

    if score > lowest_high_score:
        selecting_initials = True
        while selecting_initials:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        initials[index] = alphabet[(alphabet.index(initials[index]) - 1) % 26]
                    elif event.key == pygame.K_RIGHT:
                        initials[index] = alphabet[(alphabet.index(initials[index]) + 1) % 26]
                    elif event.key == pygame.K_RETURN:
                        if index < 2:
                            index += 1
                        else:
                            selecting_initials = False
                            name = "".join(initials)
                            high_scores.append((name, score))
                            high_scores.sort(key=lambda x: x[1], reverse=True)
                            high_scores = high_scores[:10]
                            with open(high_score_file_path, 'w') as f:
                                for name, score in high_scores:
                                    f.write(f"{name} {score}\n")

            screen.fill(BACKDROP)
            initials_text = font.render(f"New High Score! Enter initials: {' '.join(initials)}", True, score_color)
            directions_text = font.render("Use left and right arrows to change, Enter to confirm", True, score_color)

            screen.blit(initials_text, (WIDTH // 6, HEIGHT // 3))
            screen.blit(directions_text, (WIDTH // 6, HEIGHT // 3 + 40))

            pygame.display.flip()
    game_over_text = font.render("Game Over! Play again? (Y/N)", True, score_color)
    screen.blit(game_over_text, (WIDTH // 4, HEIGHT // 3 + 100))
    pygame.display.flip()


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    pygame.quit()
                    return False

# self explanatory function name
def show_high_scores():
    global high_scores
    font = pygame.font.Font(None, 36)
    score_color = (128, 0, 128)
    screen.fill(BACKDROP)
    title_text = font.render("High Scores", True, score_color)
    screen.blit(title_text, (WIDTH // 4, 10))

    y_offset = 50
    for idx, (name, score) in enumerate(high_scores):
        score_text = font.render(f"{idx + 1}. {name}: {score}", True, score_color)
        screen.blit(score_text, (WIDTH // 4, 10 + y_offset))
        y_offset += 40

    if score > high_scores[-1][1]:  # check if this score is a new high score
        name = "AAA"

        #high_scores.append((name, score))
        #high_scores.sort(key=lambda x: x[1], reverse=True)
        #high_scores = high_scores[:10]  # keep only top 10
        #with open(high_score_file_path, 'w') as f:
        #    for name, score in high_scores:
        #        f.write(f"{name} {score}\n")

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

    pygame.display.flip()


def initialize_game():
    global score, trumpys, spawn_timer, rex_rect, high_scores
    score = 0
    trumpys = [Trumpy(trumpy_img.get_rect(topleft=(WIDTH + 100, HEIGHT - 100)))]
    spawn_timer = pygame.time.get_ticks() + random.randint(min_spawn_delay, max_spawn_delay)
    rex_rect.topleft = (50, HEIGHT - 5)

    try:
        with open(high_score_file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                splitted = line.strip().split()
                if len(splitted) == 2:
                    name, high_score_str = splitted  # Using a different variable name here
                    high_scores.append((name, int(high_score_str)))
    except Exception as e:
        print(f"Error reading high score file: {e}")

# the meat
def main_game():
    global running, in_jump, vertical_speed, score, trumpys, spawn_timer, dashed_line_offset, high_scores
    initialize_game()
    # getting cloudy in here
    clouds = [Cloud(cloud_img.get_rect(topleft=(random.randint(0, WIDTH), random.randint(0, HEIGHT//2)))) for _ in range(5)]

    while running:
        screen.fill(BACKDROP)
        # add a sun
        pygame.draw.circle(screen, (255, 255, 0), (WIDTH - 50, 50), 30)
        pygame.draw.rect(screen, GROUND_COLOR, (0, ground, WIDTH, HEIGHT - ground))
        # sun rays
        sun_x, sun_y = WIDTH - 50, 50
        ray_length = 50
        for angle in range(0, 360, 15):  # Every 15 degrees
            end_x = sun_x + ray_length * math.cos(math.radians(angle))
            end_y = sun_y + ray_length * math.sin(math.radians(angle))
            pygame.draw.line(screen, (255, 255, 0), (sun_x, sun_y), (end_x, end_y), 2)
        for cloud in clouds:
            cloud.rect.x -= CLOUD_SPEED
            if cloud.rect.x + cloud.rect.width < 0:
                cloud.rect.x = WIDTH
                cloud.rect.y = random.randint(0, HEIGHT // 2)
            screen.blit(cloud_img, cloud.rect)


        # the ground aka road
        pygame.draw.rect(screen, GROUND_COLOR, (0, ground, WIDTH, HEIGHT - ground))
        # add white lines to the road
        dashed_line_length = 40
        dashed_line_width = 5
        dashed_line_gap = 20
        dashed_line_offset += int(round(SPEED / 2))
        dashed_line_y = ground + (HEIGHT - ground) // 2  # Vertically center on the road
        if dashed_line_offset > dashed_line_length + dashed_line_gap:
            dashed_line_offset = 0

        for x in range(0 - dashed_line_offset, WIDTH, dashed_line_length + dashed_line_gap):
            pygame.draw.rect(screen, (255, 255, 255), (x, dashed_line_y, dashed_line_length, dashed_line_width))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and rex_rect.y == ground - rex_rect.height:
                vertical_speed = JUMP_STRENGTH
                in_jump = True

        # rex physics
        if in_jump:
            vertical_speed += GRAVITY
            rex_rect.y += vertical_speed
        if rex_rect.y > ground - rex_rect.height:
            rex_rect.y = ground - rex_rect.height
            in_jump = False

        # trumpy physics
        current_time = pygame.time.get_ticks()
        if current_time - spawn_timer > 0:
            spawn_timer = current_time + random.randint(min_spawn_delay, max_spawn_delay)
            trumpys.append(Trumpy(trumpy_img.get_rect(topleft=(WIDTH + 100, HEIGHT - 100))))

        for trumpy in trumpys:
            trumpy.rect.x -= SPEED

        trumpys = [t for t in trumpys if t.rect.x + t.rect.width > 0]

        for trumpy in trumpys:
            if rex_rect.colliderect(trumpy.rect):
                restart = game_over_screen(score)
                if restart:
                    show_high_scores()
                    pygame.time.delay(2000)
                    initialize_game()  # Reset the game state if the player wants to continue
                else:
                    pygame.time.delay(2000)
                    running = False  # Stop the game loop if the player doesn't want to continue
                    return False
            elif trumpy.rect.x + trumpy.rect.width < rex_rect.x and not trumpy.passed:
                trumpy.passed = True
                score += 1
                highest_score = high_scores[0][1] if high_scores else 0

        for trumpy in trumpys:
            screen.blit(trumpy_img, trumpy.rect)
        screen.blit(rex_img, rex_rect)


        # score board
        font = pygame.font.Font(None, 36)
        score_color = (128, 0, 128)  # purple-ish
        score_text = font.render(f"Total fuck bois jumped: {score}", True, score_color)
        screen.blit(score_text, (10, 10))
        highest_score = high_scores[0][1] if high_scores else 0
        high_score_text = font.render(f"High Score: {highest_score}", True, score_color)
        gap = 5
        new_y_position = 10 + score_text.get_height() + gap
        screen.blit(high_score_text, (10, new_y_position))


        pygame.display.flip()
        clock.tick(60)

restart = True
while restart:
    restart = main_game()
