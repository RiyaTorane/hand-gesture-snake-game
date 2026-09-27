import cv2
import mediapipe as mp
import pygame
import random
import sys


# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()


# ============================================================
# GAME SETTINGS
# ============================================================

GAME_WIDTH = 800
GAME_HEIGHT = 600

CELL_SIZE = 20

CAM_WIDTH = 320
CAM_HEIGHT = 240

WINDOW_WIDTH = GAME_WIDTH + CAM_WIDTH
WINDOW_HEIGHT = GAME_HEIGHT


# ============================================================
# CREATE WINDOW
# ============================================================

screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

pygame.display.set_caption(
    "Snake Game - Hand Gesture Control"
)


clock = pygame.time.Clock()


# ============================================================
# COLORS
# ============================================================

BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
GRAY = (70, 70, 70)
YELLOW = (255, 255, 0)


# ============================================================
# FONTS
# ============================================================

font = pygame.font.SysFont(
    "Arial",
    25
)

small_font = pygame.font.SysFont(
    "Arial",
    18
)


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands

mp_draw = mp.solutions.drawing_utils


hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Could not open webcam.")

    pygame.quit()

    sys.exit()


cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAM_WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAM_HEIGHT
)


# ============================================================
# CREATE FOOD
# ============================================================

def create_food(snake):

    while True:

        x = random.randrange(
            0,
            GAME_WIDTH,
            CELL_SIZE
        )

        y = random.randrange(
            0,
            GAME_HEIGHT,
            CELL_SIZE
        )

        if [x, y] not in snake:

            return [x, y]


# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    snake = [
        [400, 300],
        [380, 300],
        [360, 300]
    ]

    direction = "RIGHT"

    food = create_food(snake)

    score = 0

    return snake, direction, food, score


# ============================================================
# INITIAL GAME STATE
# ============================================================

snake, direction, food, score = reset_game()


# ============================================================
# HAND MOVEMENT VARIABLES
# ============================================================

previous_x = None
previous_y = None

MOVEMENT_THRESHOLD = 20


# ============================================================
# MAIN LOOP
# ============================================================

running = True


while running:


    # ========================================================
    # PYGAME EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        if event.type == pygame.KEYDOWN:


            # ------------------------------------------------
            # QUIT
            # ------------------------------------------------

            if event.key == pygame.K_q:

                running = False


            elif event.key == pygame.K_ESCAPE:

                running = False


            # ------------------------------------------------
            # KEYBOARD BACKUP CONTROLS
            # ------------------------------------------------

            elif event.key == pygame.K_UP:

                if direction != "DOWN":

                    direction = "UP"


            elif event.key == pygame.K_DOWN:

                if direction != "UP":

                    direction = "DOWN"


            elif event.key == pygame.K_LEFT:

                if direction != "RIGHT":

                    direction = "LEFT"


            elif event.key == pygame.K_RIGHT:

                if direction != "LEFT":

                    direction = "RIGHT"


    # ========================================================
    # READ WEBCAM
    # ========================================================

    success, frame = cap.read()


    if not success:

        print("Could not read webcam.")

        break


    # Mirror webcam
    frame = cv2.flip(
        frame,
        1
    )


    # Resize webcam
    frame = cv2.resize(
        frame,
        (
            CAM_WIDTH,
            CAM_HEIGHT
        )
    )


    # ========================================================
    # MEDIAPIPE PROCESSING
    # ========================================================

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    results = hands.process(
        rgb_frame
    )


    # ========================================================
    # HAND DETECTION
    # ========================================================

    if results.multi_hand_landmarks:


        for hand_landmarks in results.multi_hand_landmarks:


            # ------------------------------------------------
            # DRAW HAND LANDMARKS
            # ------------------------------------------------

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )


            # ------------------------------------------------
            # INDEX FINGER
            # ------------------------------------------------

            index_finger = hand_landmarks.landmark[8]


            current_x = int(
                index_finger.x * CAM_WIDTH
            )

            current_y = int(
                index_finger.y * CAM_HEIGHT
            )


            # ------------------------------------------------
            # DRAW INDEX FINGER TIP
            # ------------------------------------------------

            cv2.circle(
                frame,
                (
                    current_x,
                    current_y
                ),
                8,
                (0, 255, 0),
                -1
            )


            # =================================================
            # DETECT MOVEMENT
            # =================================================

            if previous_x is not None and previous_y is not None:


                dx = current_x - previous_x

                dy = current_y - previous_y


                # ------------------------------------------------
                # HORIZONTAL MOVEMENT
                # ------------------------------------------------

                if abs(dx) > abs(dy):


                    if abs(dx) > MOVEMENT_THRESHOLD:


                        # Move RIGHT
                        if dx > 0:


                            if direction != "LEFT":

                                direction = "RIGHT"


                        # Move LEFT
                        else:


                            if direction != "RIGHT":

                                direction = "LEFT"


                # ------------------------------------------------
                # VERTICAL MOVEMENT
                # ------------------------------------------------

                else:


                    if abs(dy) > MOVEMENT_THRESHOLD:


                        # Move DOWN
                        if dy > 0:


                            if direction != "UP":

                                direction = "DOWN"


                        # Move UP
                        else:


                            if direction != "DOWN":

                                direction = "UP"


            previous_x = current_x

            previous_y = current_y


    else:

        previous_x = None

        previous_y = None


    # ========================================================
    # MOVE SNAKE
    # ========================================================

    head_x = snake[0][0]

    head_y = snake[0][1]


    if direction == "UP":

        head_y -= CELL_SIZE


    elif direction == "DOWN":

        head_y += CELL_SIZE


    elif direction == "LEFT":

        head_x -= CELL_SIZE


    elif direction == "RIGHT":

        head_x += CELL_SIZE


    # ========================================================
    # EDGE WRAPPING
    # ========================================================

    # Right edge → left edge
    if head_x >= GAME_WIDTH:

        head_x = 0


    # Left edge → right edge
    elif head_x < 0:

        head_x = GAME_WIDTH - CELL_SIZE


    # Bottom edge → top edge
    if head_y >= GAME_HEIGHT:

        head_y = 0


    # Top edge → bottom edge
    elif head_y < 0:

        head_y = GAME_HEIGHT - CELL_SIZE


    new_head = [
        head_x,
        head_y
    ]


    # ========================================================
    # BODY COLLISION
    # ========================================================

    if new_head in snake:

        snake, direction, food, score = reset_game()

        previous_x = None

        previous_y = None

        continue


    # ========================================================
    # ADD NEW HEAD
    # ========================================================

    snake.insert(
        0,
        new_head
    )


    # ========================================================
    # FOOD COLLISION
    # ========================================================

    if new_head == food:


        score += 1

        food = create_food(
            snake
        )


    else:

        snake.pop()


    # ========================================================
    # DRAW GAME
    # ========================================================

    screen.fill(
        BLACK
    )


    # ========================================================
    # DRAW GAME BORDER
    # ========================================================

    pygame.draw.rect(
        screen,
        GRAY,
        (
            0,
            0,
            GAME_WIDTH,
            GAME_HEIGHT
        ),
        2
    )


    # ========================================================
    # DRAW SNAKE
    # ========================================================

    for i, segment in enumerate(snake):


        x = segment[0]

        y = segment[1]


        if i == 0:

            # Snake head
            pygame.draw.rect(
                screen,
                GREEN,
                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )
            )

        else:

            # Snake body
            pygame.draw.rect(
                screen,
                DARK_GREEN,
                (
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )
            )


    # ========================================================
    # DRAW FOOD
    # ========================================================

    pygame.draw.rect(
        screen,
        RED,
        (
            food[0],
            food[1],
            CELL_SIZE,
            CELL_SIZE
        )
    )


    # ========================================================
    # CAMERA
    # ========================================================

    camera_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    camera_surface = pygame.surfarray.make_surface(
        camera_rgb.swapaxes(
            0,
            1
        )
    )


    # Display camera
    screen.blit(
        camera_surface,
        (
            GAME_WIDTH,
            0
        )
    )


    # ========================================================
    # CAMERA BORDER
    # ========================================================

    pygame.draw.rect(
        screen,
        BLUE,
        (
            GAME_WIDTH,
            0,
            CAM_WIDTH,
            CAM_HEIGHT
        ),
        3
    )


    # ========================================================
    # SCORE
    # ========================================================

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )


    screen.blit(
        score_text,
        (
            10,
            10
        )
    )


    # ========================================================
    # DIRECTION
    # ========================================================

    direction_text = font.render(
        f"Direction: {direction}",
        True,
        WHITE
    )


    screen.blit(
        direction_text,
        (
            10,
            40
        )
    )


    # ========================================================
    # CAMERA TITLE
    # ========================================================

    camera_title = font.render(
        "LIVE CAMERA",
        True,
        WHITE
    )


    screen.blit(
        camera_title,
        (
            GAME_WIDTH + 80,
            CAM_HEIGHT + 15
        )
    )


    # ========================================================
    # CONTROLS
    # ========================================================

    instruction1 = small_font.render(
        "Move your index finger",
        True,
        WHITE
    )


    screen.blit(
        instruction1,
        (
            GAME_WIDTH + 65,
            CAM_HEIGHT + 50
        )
    )


    instruction2 = small_font.render(
        "Arrow keys = backup control",
        True,
        WHITE
    )


    screen.blit(
        instruction2,
        (
            GAME_WIDTH + 45,
            CAM_HEIGHT + 75
        )
    )


    instruction3 = small_font.render(
        "Q / ESC = Quit",
        True,
        YELLOW
    )


    screen.blit(
        instruction3,
        (
            GAME_WIDTH + 90,
            CAM_HEIGHT + 100
        )
    )


    # ========================================================
    # EDGE WRAP INFORMATION
    # ========================================================

    wrap_text = small_font.render(
        "Edges wrap around",
        True,
        GREEN
    )


    screen.blit(
        wrap_text,
        (
            GAME_WIDTH + 75,
            CAM_HEIGHT + 135
        )
    )


    # ========================================================
    # UPDATE SCREEN
    # ========================================================

    pygame.display.update()


    # ========================================================
    # GAME SPEED
    # ========================================================

    clock.tick(10)


# ============================================================
# CLEANUP
# ============================================================

cap.release()

hands.close()

cv2.destroyAllWindows()

pygame.quit()

sys.exit()

