import pyautogui as gui
import keyboard
import time
import numpy as np
import random

# Define the actions
actions = ['jump', 'nothing']

q_table = {}  # Use a dictionary for dynamic Q-table

# Q-learning settings
learning_rate = 0.15
discount_factor = 0.95
epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay = 0.995
epsilon = epsilon_start  # Exploration rate

def choose_action(state):
    global epsilon
    # Ensure the state is in the Q-table
    if state not in q_table:
        q_table[state] = np.zeros(len(actions))

    if random.uniform(0, 1) < epsilon:
        action = random.choice(actions)  # Explore action space
    else:
        action = actions[np.argmax(q_table[state])]  # Exploit learned values
    epsilon = max(epsilon_end, epsilon_decay * epsilon)  # Decay epsilon
    return action

def update_q_table(state, action, reward, next_state):
    # Ensure the state-action pair is in the Q-table
    if state not in q_table:
        q_table[state] = np.zeros(len(actions))
    if next_state not in q_table:
        q_table[next_state] = np.zeros(len(actions))

    old_value = q_table[state][actions.index(action)]
    next_max = np.max(q_table[next_state])

    # Q-learning formula
    new_value = (1 - learning_rate) * old_value + learning_rate * (reward + discount_factor * next_max)
    q_table[state][actions.index(action)] = new_value

def calculate_distance_to_obstacle():
    global x_start, x_end  # Use the global variables for obstacle detection range

    sct_img = gui.screenshot(region=(0, 102, 1920, 872))
    bg_color = sct_img.getpixel((100, 100))  # Same as in is_obstacle_present

    for i in range(x_start, x_end):
        if sct_img.getpixel((i, 557)) != bg_color or sct_img.getpixel((i, 486)) != bg_color:
            # Found the nearest obstacle, calculate distance from the dinosaur
            distance = i - 131  # Dinosaur's x-coordinate is 131
            return max(distance, 0)  # Ensure distance is not negative

    return None  # No obstacle found in the current range

def get_state():
    distance_to_obstacle = calculate_distance_to_obstacle()
    if distance_to_obstacle is None:
        distance_to_obstacle = -1  # Default value if no obstacle is found

    time_elapsed = int(time.time() - start_time)
    return (distance_to_obstacle, time_elapsed)

def perform_action(action):
    if action == 'jump':
        keyboard.press('up')
        time.sleep(0.1)
        keyboard.release('up')

def is_obstacle_present(sct_img, bg_color, x_start, x_end, y_search1, y_search2):
    for i in range(x_start, x_end):
        if sct_img.getpixel((i, y_search1)) != bg_color or sct_img.getpixel((i, y_search2)) != bg_color:
            return True  # Obstacle detected
    return False

def check_game_over(bg_color):
    # Coordinates for the game over text area
    x, y, width, height = 911, 555, 50, 60  # Adjust width and height if needed
    check_img = gui.screenshot(region=(x, y, width, height))

    for i in range(width):
        for j in range(height):
            if check_img.getpixel((i, j)) == bg_color:  # Check if the pixel matches the background color
                return False  # Background color found, so the game is not over
    return True  # No background color found in the region, game over

def start():
    time.sleep(1)
    global start_time, last_action, x_start, x_end, last_state
    start_time = time.time()
    last_update = start_time
    last_action = 'nothing'
    x_start,x_end = 300, 420
    last_reward_time = start_time  # Track last time a survival reward was given

    while True:
        if keyboard.is_pressed('q'):  # Quit the program
            break

        reward=0
        sct_img = gui.screenshot(region=(0, 102, 1920, 872))
        bg_color = sct_img.getpixel((100, 100))

        current_time = time.time() - start_time

        if is_obstacle_present(sct_img, bg_color, x_start, x_end, 557, 486):
            last_state = get_state()
            action = choose_action(last_state)
            perform_action(action)
            last_action = action
        else:
            last_action = 'nothing'  # No action if no obstacle
            last_state = get_state()

        # Survival reward
        if time.time() - last_reward_time >= 0.5:
            reward = 30  # Reward for surviving .5 seconds
            update_q_table(last_state, last_action, reward, get_state())
            last_reward_time = time.time()  # Update the last reward time
            x_end+=2

        if check_game_over(bg_color):
            # Game over logic
            reward = -200  # Negative reward for losing
            state = get_state()
            update_q_table(last_state, last_action, reward, 0)
            start_time = time.time()  # Reset the time
            last_reward_time = start_time  # Reset survival reward timer
            gui.click(960, 579)  # Restart the game
            x_end = 420
            continue

start()