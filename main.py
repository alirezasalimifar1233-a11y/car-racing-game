import pygame
import random
import json
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("بازی ماشین")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 46)

WHITE = (255, 255, 255)
BLACK = (15, 15, 15)
GRAY = (90, 90, 90)
GREEN = (30, 180, 70)
RED = (220, 40, 40)
BLUE = (30, 100, 240)
YELLOW = (255, 210, 0)
PURPLE = (150, 50, 220)
GOLD = (255, 190, 0)

DATA_FILE = os.path.join(os.path.expanduser("\~"), "car_data.json")

coins = 0
best = 0
owned_cars = [0]
selected_car = 0

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump({
                "coins": coins,
                "best": best,
                "owned_cars": owned_cars,
                "selected_car": selected_car
            }, f)
    except:
        pass

def load_data():
    global coins, best, owned_cars, selected_car
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
        coins = int(d.get("coins", 0))
        best = int(d.get("best", 0))
        owned_cars = d.get("owned_cars", [0])
        selected_car = int(d.get("selected_car", 0))
    except:
        pass
    if 0 not in owned_cars:
        owned_cars.insert(0, 0)
    owned_cars = [i for i in owned_cars if isinstance(i, int) and 0 <= i < 5]
    if selected_car not in owned_cars:
        selected_car = 0

load_data()

# ==================== صدا ====================
engine_sound = None
crash_sound = None
engine_playing = False

engine_paths = [
    "/storage/emulated/0/Download/Car-Acceleration-Sound-3.mp3",
    "/storage/emulated/0/Download/engine.mp3",
    "Car-Acceleration-Sound-3.mp3",
    "engine.mp3"
]

crash_paths = [
    "/storage/emulated/0/Download/crash.mp3",
    "/storage/emulated/0/Download/crash.wav",
    "crash.mp3",
    "crash.wav"
]

for path in engine_paths:
    try:
        if os.path.exists(path):
            engine_sound = pygame.mixer.Sound(path)
            engine_sound.set_volume(0.35)
            break
    except:
        pass

for path in crash_paths:
    try:
        if os.path.exists(path):
            crash_sound = pygame.mixer.Sound(path)
            crash_sound.set_volume(0.85)
            break
    except:
        pass

def start_engine():
    global engine_playing
    if engine_sound and not engine_playing:
        engine_sound.play(loops=-1)
        engine_playing = True

def stop_engine():
    global engine_playing
    if engine_sound and engine_playing:
        engine_sound.stop()
        engine_playing = False

def play_crash():
    if crash_sound:
        crash_sound.play()

def update_engine_volume(current_speed):
    """هر چی سرعت بالاتر بره صدای موتور هم بلندتر می‌شه"""
    if engine_sound and engine_playing:
        # سرعت از ۵ تا ۱۳ → حجم از ۰.۳۰ تا ۰.۷۵
        vol = 0.30 + (current_speed - 5) * 0.05
        vol = max(0.25, min(0.75, vol))
        engine_sound.set_volume(vol)
# ==============================================

car_colors = [RED, BLUE, YELLOW, WHITE, PURPLE]
car_names = ["RED", "BLUE", "YELLOW", "WHITE", "PURPLE"]
car_prices = [0, 10, 25, 40, 60]

left_button = pygame.Rect(15, 605, 105, 75)
right_button = pygame.Rect(130, 605, 105, 75)
pause_button = pygame.Rect(305, 12, 83, 45)

start_button = pygame.Rect(70, 290, 260, 65)
shop_button = pygame.Rect(70, 375, 260, 65)
back_button = pygame.Rect(20, 20, 100, 45)
buy_button = pygame.Rect(45, 500, 310, 65)
prev_button = pygame.Rect(25, 340, 65, 60)
next_button = pygame.Rect(310, 340, 65, 60)
resume_button = pygame.Rect(60, 310, 280, 65)
menu_button = pygame.Rect(60, 395, 280, 60)
restart_button = pygame.Rect(60, 380, 280, 60)

LANES = [85, 175, 265]
player_lane = 1

state = "MENU"
player = pygame.Rect(LANES[1], 490, 50, 80)
enemies = []
road_coins = []
score = 0
speed = 6.5          # سرعت پایه بالاتر
road_offset = 0
spawn_timer = 0
coin_timer = 0
shop_index = 0

def reset_game():
    global player, enemies, road_coins, score, speed, road_offset, spawn_timer, coin_timer, player_lane
    player_lane = 1
    player = pygame.Rect(LANES[1], 490, 50, 80)
    enemies = []
    road_coins = []
    score = 0
    speed = 6.5
    road_offset = 0
    spawn_timer = 0
    coin_timer = 0

def draw_text(text, x, y, color=WHITE, f=None, center=False):
    img = (f or font).render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)

def draw_button(rect, text, color=BLUE):
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)
    draw_text(text, rect.centerx, rect.centery, WHITE, center=True)

def draw_car(rect, index, is_player=False):
    color = car_colors[index]
    for y in (rect.y + 12, rect.bottom - 28):
        pygame.draw.rect(screen, BLACK, (rect.x - 4, y, 8, 18), border_radius=3)
        pygame.draw.rect(screen, BLACK, (rect.right - 4, y, 8, 18), border_radius=3)
    pygame.draw.rect(screen, color, rect, border_radius=9)
    pygame.draw.rect(screen, (120, 210, 240), (rect.x + 8, rect.y + 12, rect.width - 16, 22), border_radius=5)
    pygame.draw.rect(screen, (30, 30, 30), (rect.x + 8, rect.y + 42, rect.width - 16, 18), border_radius=4)
    pygame.draw.rect(screen, YELLOW, (rect.x + 5, rect.y + 3, 10, 6))
    pygame.draw.rect(screen, YELLOW, (rect.right - 15, rect.y + 3, 10, 6))

def draw_road():
    global road_offset
    screen.fill((35, 125, 45))
    pygame.draw.rect(screen, (55, 55, 55), (45, 0, 310, HEIGHT))
    pygame.draw.line(screen, WHITE, (50, 0), (50, HEIGHT), 5)
    pygame.draw.line(screen, WHITE, (350, 0), (350, HEIGHT), 5)
    road_offset = (road_offset + speed) % 80
    for y in range(-80, HEIGHT + 80, 80):
        yy = y + road_offset
        pygame.draw.rect(screen, WHITE, (145, yy, 6, 42))
        pygame.draw.rect(screen, WHITE, (249, yy, 6, 42))

def draw_coin(rect):
    pygame.draw.circle(screen, (160, 100, 0), rect.center, 13)
    pygame.draw.circle(screen, GOLD, rect.center, 10)
    pygame.draw.circle(screen, (255, 240, 100), rect.center, 6)
    draw_text("$", rect.centerx, rect.centery, (130, 80, 0), center=True)

def draw_game_scene():
    draw_road()
    for c in road_coins:
        draw_coin(c)
    for e in enemies:
        draw_car(e, 1)
    draw_car(player, selected_car, True)
    draw_text("Score: " + str(score), 10, 12)
    draw_text("Coins: " + str(coins), 10, 42, GOLD)
    draw_text("Level: " + str(score // 10 + 1), 10, 72)
    draw_button(left_button, "<")
    draw_button(right_button, ">")
    draw_button(pause_button, "PAUSE", RED)

def draw_menu():
    screen.fill((20, 30, 50))
    draw_text("CAR RACING", 200, 130, YELLOW, big_font, True)
    draw_text("Coins: " + str(coins), 200, 205, GOLD, center=True)
    draw_button(start_button, "START GAME", GREEN)
    draw_button(shop_button, "CAR SHOP")
    draw_text("Best: " + str(best), 200, 480, WHITE, center=True)

def draw_shop():
    screen.fill((25, 25, 45))
    draw_button(back_button, "BACK", RED)
    draw_text("CAR SHOP", 200, 105, YELLOW, big_font, True)
    draw_text("Coins: " + str(coins), 200, 160, GOLD, center=True)
    draw_text(car_names[shop_index], 200, 240, WHITE, center=True)
    draw_car(pygame.Rect(175, 280, 50, 80), shop_index, shop_index == 0)
    draw_button(prev_button, "<")
    draw_button(next_button, ">")
    if shop_index in owned_cars:
        label = "SELECTED" if selected_car == shop_index else "SELECT CAR"
        color = GRAY if selected_car == shop_index else GREEN
    else:
        label = "BUY: " + str(car_prices[shop_index]) + " COINS"
        color = GOLD
    draw_button(buy_button, label, color)
    draw_text("Car " + str(shop_index + 1) + " / 5", 200, 600, WHITE, center=True)

def draw_overlay(title, title_color):
    draw_game_scene()
    shade = pygame.Surface((WIDTH, HEIGHT))
    shade.set_alpha(185)
    shade.fill((0, 0, 0))
    screen.blit(shade, (0, 0))
    draw_text(title, 200, 230, title_color, big_font, True)

running = True
try:
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "GAME":
                        state = "PAUSE"
                        stop_engine()
                    elif state == "PAUSE":
                        state = "GAME"
                        start_engine()
                if state == "GAME":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        if player_lane > 0:
                            player_lane -= 1
                            player.x = LANES[player_lane]
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        if player_lane < 2:
                            player_lane += 1
                            player.x = LANES[player_lane]

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if state == "MENU":
                    if start_button.collidepoint(x, y):
                        reset_game()
                        state = "GAME"
                        start_engine()
                    elif shop_button.collidepoint(x, y):
                        state = "SHOP"

                elif state == "SHOP":
                    if back_button.collidepoint(x, y):
                        state = "MENU"
                    elif prev_button.collidepoint(x, y):
                        shop_index = (shop_index - 1) % 5
                    elif next_button.collidepoint(x, y):
                        shop_index = (shop_index + 1) % 5
                    elif buy_button.collidepoint(x, y):
                        if shop_index in owned_cars:
                            selected_car = shop_index
                            save_data()
                        elif coins >= car_prices[shop_index]:
                            coins -= car_prices[shop_index]
                            owned_cars.append(shop_index)
                            selected_car = shop_index
                            save_data()

                elif state == "GAME":
                    if pause_button.collidepoint(x, y):
                        state = "PAUSE"
                        stop_engine()
                    elif left_button.collidepoint(x, y):
                        if player_lane > 0:
                            player_lane -= 1
                            player.x = LANES[player_lane]
                    elif right_button.collidepoint(x, y):
                        if player_lane < 2:
                            player_lane += 1
                            player.x = LANES[player_lane]

                elif state == "PAUSE":
                    if resume_button.collidepoint(x, y):
                        state = "GAME"
                        start_engine()
                    elif menu_button.collidepoint(x, y):
                        stop_engine()
                        save_data()
                        state = "MENU"

                elif state == "GAME_OVER":
                    if restart_button.collidepoint(x, y):
                        reset_game()
                        state = "GAME"
                        start_engine()
                    elif menu_button.collidepoint(x, y):
                        stop_engine()
                        save_data()
                        state = "MENU"

        if state == "GAME":
            spawn_timer += 1
            if spawn_timer >= max(14, 36 - score // 6):
                enemies.append(pygame.Rect(random.choice(LANES), -90, 45, 75))
                spawn_timer = 0

            coin_timer += 1
            if coin_timer >= 60:
                road_coins.append(pygame.Rect(random.choice(LANES) + 10, -25, 25, 25))
                coin_timer = 0

            for e in enemies[:]:
                e.y += speed
                if e.top > HEIGHT:
                    enemies.remove(e)
                    score += 1
                elif player.colliderect(e):
                    play_crash()
                    stop_engine()
                    state = "GAME_OVER"
                    best = max(best, score)
                    save_data()

            for c in road_coins[:]:
                c.y += speed
                if player.colliderect(c):
                    coins += 1
                    road_coins.remove(c)
                    save_data()
                elif c.top > HEIGHT:
                    road_coins.remove(c)

            # سرعت با امتیاز بالا می‌ره (هماهنگ با صدای موتور)
            speed = min(14.5, 6.5 + score // 8)
            update_engine_volume(speed)

        if state == "MENU":
            draw_menu()
        elif state == "SHOP":
            draw_shop()
        elif state == "GAME":
            draw_game_scene()
        elif state == "PAUSE":
            draw_overlay("PAUSED", YELLOW)
            draw_button(resume_button, "RESUME", GREEN)
            draw_button(menu_button, "MAIN MENU")
        elif state == "GAME_OVER":
            draw_overlay("GAME OVER", RED)
            draw_text("Score: " + str(score), 200, 300, WHITE, center=True)
            draw_button(restart_button, "PLAY AGAIN", GREEN)
            draw_button(menu_button, "MAIN MENU")

        pygame.display.flip()

finally:
    stop_engine()
    save_data()
    pygame.quit()
  
