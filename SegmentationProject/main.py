import pygame
import sys
import random
import cv2
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
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

# Scores
player_score, opponent_score = 0, 0

# Ball
ball = pygame.Rect(0, 0, 20, 20)
ball.center = (WIDTH / 2, HEIGHT / 2)

# Speeds
x_speed, y_speed = 4, 4  # Increased initial speed

def reset_ball():
    ball.center = (WIDTH / 2, HEIGHT / 2)
    global x_speed, y_speed
    x_speed = random.choice([4, -4])  # Reset speed to original values
    y_speed = random.choice([4, -4])

# Initialize the camera
cap = cv2.VideoCapture(0)

while True:
    # Capture frame from camera
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert the frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the range for dark green color
    lower_green = np.array([35, 100, 20])  # Lower bound for dark green
    upper_green = np.array([85, 255, 100])  # Upper bound for dark green

    # Create a mask for the green color
    mask = cv2.inRange(hsv_frame, lower_green, upper_green)

    # Find contours of the masked area
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the largest contour
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the bounding box of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate the center of the bounding box
        green_center = (x + w // 2, y + h // 2)

        # Move the player's paddle based on the y-coordinate of the green object
        player.centery = green_center[1]
        # Clamp the player's paddle within the screen bounds
        if player.top < 0:
            player.top = 0
        if player.bottom > HEIGHT:
            player.bottom = HEIGHT

    # Ball movement logic
    ball.x += x_speed
    ball.y += y_speed

    if ball.y >= HEIGHT or ball.y <= 0:
        y_speed = -y_speed  # Reverse direction if hitting top or bottom

    if ball.x <= 0:
        player_score += 1
        reset_ball()
    if ball.x >= WIDTH:
        opponent_score += 1
        reset_ball()

    # Paddle collision detection
    if player.colliderect(ball):
        x_speed = -x_speed
        ball.x = player.right  # Prevent the ball from sticking

    if opponent.colliderect(ball):
        x_speed = -x_speed
        ball.x = opponent.left - ball.width  # Prevent the ball from sticking

    # AI movement
    if opponent.y < ball.y:
        opponent.top += 3
    if opponent.bottom > ball.y:
        opponent.bottom -= 3

    # Draw everything
    SCREEN.fill("Black")
    pygame.draw.rect(SCREEN, "white", player)
    pygame.draw.rect(SCREEN, "white", opponent)
    pygame.draw.ellipse(SCREEN, "white", ball)

    # Draw scores
    player_score_text = FONT.render(str(player_score), True, "white")
    opponent_score_text = FONT.render(str(opponent_score), True, "white")
    SCREEN.blit(player_score_text, (WIDTH / 2 + 50, 50))
    SCREEN.blit(opponent_score_text, (WIDTH / 2 - 50, 50))

    # Show the mask and original feed in separate OpenCV windows
    cv2.imshow("Green Color Detection", mask)
    cv2.imshow("Original Camera Feed", frame)

    # Update the display
    pygame.display.update()

    # Handle quitting
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()

    CLOCK.tick(60)  # Adjust frame rate to a reasonable value

# Release the camera when done
cap.release()
cv2.destroyAllWindows()
