import pygame, sys, random
import cv2
import numpy as np

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
capture = cv2.VideoCapture(0)

while True:
    ret, frame = capture.read()
    #making it so the camera is not mirrored
    frame = cv2.flip(frame, 1)

    if not ret:
        print("not able to grab frame")
        continue

    #makes it so the frame goes from rgb to hsv
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #lower threshold for green
    lower_green = np.array([35, 100, 50])
    #upper threshold for green
    upper_green = np.array([85, 255, 255])

    #this is for red, since red is in the beginning and end of the hsv color graph then u need 2 different ranges
    lower_red_1 = np.array([0, 150, 150])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([170, 150, 150])
    upper_red_2 = np.array([180, 255, 255])

    #mask the objects, shows in white our color and black the rest
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_red_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask_red_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

    #combine masks
    mask_red = mask_red_1 | mask_red_2

    #shows the actual color of the object instead of just white
    green_segmentation = cv2.bitwise_and(frame, frame, mask=mask_green)
    blue_segmentation = cv2.bitwise_and(frame, frame, mask=mask_red)

    #finds all the points that make up the contour of the "color block"
    #cv2.RETR_EXTERNAL only gets the external contour, the largest, ignoring any internal contours
    contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours2, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        #creates rectangle that bounds the largest contour found
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        #calculates center of that rectangle
        green_center = (x + w // 2, y + h // 2)
        #defines the center of that rectangle as the player object
        player.centery = green_center[1]

        #confines paddle to camera bounds
        if player.top < 0:
            player.top = 0
        if player.bottom > HEIGHT:
            player.bottom = HEIGHT

    if contours2:
        largest_contour_red = max(contours2, key=cv2.contourArea)
        a, b, c, d = cv2.boundingRect(largest_contour_red)
        cv2.rectangle(frame, (a, b), (a + c, b + d), (0, 0, 255), 2)

        red_center = (a + c // 2, b + d // 2)
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
    #show all windows in between the process
    cv2.imshow("green hsv", mask_green)
    cv2.imshow("red hsv", mask_red)
    cv2.imshow("og cam feed", frame)
    cv2.imshow("green segmentation", green_segmentation)
    cv2.imshow("red segmentation", blue_segmentation)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            capture.release()
            cv2.destroyAllWindows()
            sys.exit()

    CLOCK.tick(300)

capture.release()
cv2.destroyAllWindows()

