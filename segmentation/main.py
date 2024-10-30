import pygame, sys, random
import cv2
import numpy as np
import segmentation_function
from segmentation_function import open_camera, segmentation, contours_main, contours2_main

pygame.init()

WIDTH, HEIGHT = 1280, 720

FONT = pygame.font.SysFont("Consolas", int(WIDTH / 20))

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong!")

CLOCK = pygame.time.Clock()

# Paddles

player = pygame.Rect(0, 0, 10, 100)
player.center = (WIDTH - 100, HEIGHT / 2)

opponent = pygame.Rect(0, 0, 10, 100)
opponent.center = (100, HEIGHT / 2)

player_score, opponent_score = 0, 0

# Ball

ball = pygame.Rect(0, 0, 20, 20)
ball.center = (WIDTH / 2, HEIGHT / 2)

x_speed, y_speed = 1, 1

#stating camera
capture = open_camera()

while True:

    frame, contours, contours2 = segmentation(capture)

    if contours:
        green_center = contours_main(frame, contours)
        #defines the center of that rectangle as the player object
        player.centery = green_center[1]

        #confines paddle to camera bounds
        if player.top < 0:
            player.top = 0
        if player.bottom > HEIGHT:
            player.bottom = HEIGHT

    if contours2:
        red_center = contours2_main(frame, contours2)
        opponent.centery = red_center[1]
        if opponent.top < 0:
            opponent.top = 0
        if opponent.bottom > HEIGHT:
            opponent.bottom = HEIGHT

    if ball.y >= HEIGHT:
        y_speed = -1
    if ball.y <= 0:
        y_speed = 1
    if ball.x <= 0:
        player_score += 1
        ball.center = (WIDTH / 2, HEIGHT / 2)
        x_speed, y_speed = random.choice([1, -1]), random.choice([1, -1])
    if ball.x >= WIDTH:
        opponent_score += 1
        ball.center = (WIDTH / 2, HEIGHT / 2)
        x_speed, y_speed = random.choice([1, -1]), random.choice([1, -1])
    if player.x - ball.width <= ball.x <= player.right and ball.y in range(player.top - ball.width,
                                                                       player.bottom + ball.width):
        x_speed = -1
    if opponent.x - ball.width <= ball.x <= opponent.right and ball.y in range(opponent.top - ball.width,
                                                                           opponent.bottom + ball.width):
        x_speed = 1

    player_score_text = FONT.render(str(player_score), True, "white")
    opponent_score_text = FONT.render(str(opponent_score), True, "white")

    ball.x += x_speed * 15
    ball.y += y_speed * 15

    SCREEN.fill("Black")

    pygame.draw.rect(SCREEN, "white", player)
    pygame.draw.rect(SCREEN, "white", opponent)
    pygame.draw.circle(SCREEN, "white", ball.center, 10)

    SCREEN.blit(player_score_text, (WIDTH / 2 + 50, 50))
    SCREEN.blit(opponent_score_text, (WIDTH / 2 - 50, 50))

    pygame.display.update()

    if frame is not None:
        cv2.imshow("og cam feed", frame)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            capture.release()
            cv2.destroyAllWindows()
            sys.exit()

    CLOCK.tick(300)

capture.release()
cv2.destroyAllWindows()

