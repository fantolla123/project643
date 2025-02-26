import random
import time

import pygame
import sys
import os

pygame.init()

# ------------------------
# ПАРАМЕТРЫ ОКНА И УРОВНЯ
# ------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("игра")
clock = pygame.time.Clock()

# Общая ширина уровня (по горизонтали)
LEVEL_WIDTH = 3000
level_data = {1:
        {
        "LEVEL_WIDTH": 3000,
        "platform_layout": [
        # (x, y, w, h, тип)
        (200, 450, 150, 30, "stationary"),
        (400, 350, 120, 30, "stationary"),
        (550, 300, 120, 30, "temporary"),
        (800, 300, 150, 30, "stationary"),
        (1000, 350, 150, 30, "moving"),
        (1200, 250, 150, 30, "stationary"),
        (1400, 200, 200, 30, "stationary"),
        (1700, 250, 150, 30, "stationary"),
        (2000, 300, 150, 30, "stationary"),
        (2300, 200, 150, 30, "moving"),
        (2600, 350, 120, 30, "stationary"),
        (2800, 250, 120, 30, "stationary")],
        "coins_positions": [
        (250, 400),
        (650, 200),
        (1050, 340),
        (1250, 200),
        (1650, 200),
        (2050, 250),
        (2270, 180),
        (2630, 340),
        (2950, 200)],
        "finish_line": (2980, 0, 50, HEIGHT)},
    2: {
        "LEVEL_WIDTH": 2000,
        "platform_layout": [
            # (x, y, w, h, тип)
            (200, 450, 150, 30, "stationary"),
            (550, 330, 120, 30, "moving"),
            (940, 330, 120, 30, "temporary"),
            (1250, 300, 120, 30, "stationary"),
            (1540, 280, 100, 30, "temporary"),
            (1840, 280, 80, 30, "stationary"),
            # ... добавьте остальные платформы для уровня 2
        ],
        "coins_positions": [
            (350, 380),
            (900, 360),
            (586, 287),
            (1150, 330),
            (1050, 300),
            (1400, 340),
            # ... добавьте остальные позиции монет
        ],
        "finish_line": (1980, 0, 50, HEIGHT)
    }
}
# ------------------------
# ЗАГРУЗКА РЕСУРСОВ
# ------------------------

# 1) Фон (можно растянуть, либо отрисовывать несколько раз)
try:
    background_img = pygame.image.load(os.path.join("assets_first", "background.jpg")).convert()
    # Если хотите, можно масштабировать его под ширину уровня
    # Но обычно делают тайлинг (повтор) или параллакс. Для простоты — растянем на всю длину:
    background_img = pygame.transform.scale(background_img, (LEVEL_WIDTH, HEIGHT))
except:
    background_img = None

# 2) Изображение платформы
try:
    platform_img = pygame.image.load(os.path.join("assets_first", "platform.png")).convert_alpha()
except Exception as e:
    print("Ошибка загрузки platform.png:", e)
    sys.exit()


# 3) Игрок (спрайты)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Для упрощения — два состояния анимации (idle, run)
        try:
            self.idle_frames = [
                pygame.image.load(os.path.join("assets_first", "player", "idle1.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "idle2.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "idle3.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "idle4.png")).convert_alpha()
            ]
            self.run_frames = [

                pygame.image.load(os.path.join("assets_first", "player", "run3.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run4.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run5.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run6.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run7.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run7.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run8.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run9.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run10.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run11.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run12.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run13.png")).convert_alpha(),
                pygame.image.load(os.path.join("assets_first", "player", "run14.png")).convert_alpha()
            ]

        except Exception as e:
            print("Ошибка загрузки спрайтов игрока:", e)
            sys.exit()

        # Увеличим спрайты, если они мелкие
        scale_factor = 2
        self.idle_frames = [
            pygame.transform.scale(img, (img.get_width() * scale_factor, img.get_height() * scale_factor))
            for img in self.idle_frames
        ]
        self.run_frames = [
            pygame.transform.scale(img, (img.get_width() * scale_factor, img.get_height() * scale_factor))
            for img in self.run_frames
        ]

        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Параметры анимации
        self.frame_index = 0
        self.animation_speed = 0.15

        # Физика движения
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.direction = 1  # 1 - вправо, -1 - влево

        # Счётчик монет
        self.coins_collected = 0

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT]:
            self.vel_x = -5
            self.direction = -1
        if keys[pygame.K_RIGHT]:
            self.vel_x = 5
            self.direction = 1

        # Прыжок
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False

        # Гравитация
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10

        # Горизонтальное движение
        self.rect.x += self.vel_x
        self.horizontal_collision(platforms)

        # Вертикальное движение
        self.rect.y += self.vel_y
        self.vertical_collision(platforms)

        # Анимация
        self.animate()

    def horizontal_collision(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if getattr(platform, "is_active", True) is False:
                    continue  # временная платформа, которая уже пропала
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right

    def vertical_collision(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if isinstance(platform, TemporaryPlatform):
                    if not platform.is_active:
                        continue
                    platform.on_player_collide()
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def animate(self):
        if self.vel_x != 0:
            frames = self.run_frames
        else:
            frames = self.idle_frames

        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0

        current_frame = frames[int(self.frame_index)]
        if self.direction == -1:
            current_frame = pygame.transform.flip(current_frame, True, False)

        self.image = current_frame

    def draw(self, surface, camera_x):
        # При отрисовке учитываем смещение камеры
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


# 3 вида платформ
class StationaryPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.transform.scale(platform_img, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, x1, x2, speed=2):
        super().__init__()
        self.image = pygame.transform.scale(platform_img, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x1 = x1
        self.x2 = x2
        self.speed = speed
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.x <= self.x1:
            self.rect.x = self.x1
            self.direction = 1
        elif self.rect.x >= self.x2:
            self.rect.x = self.x2
            self.direction = -1

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class TemporaryPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, disappear_delay=2.0):
        super().__init__()
        self.image = pygame.transform.scale(platform_img, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.disappear_delay = disappear_delay
        self.is_active = True
        self.timer_started = False
        self.timer_start_time = 0

    def update(self):
        if not self.is_active:
            return
        if self.timer_started:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.timer_start_time) / 1000.0
            if elapsed >= self.disappear_delay:
                self.is_active = False

    def on_player_collide(self):
        if not self.timer_started:
            self.timer_started = True
            self.timer_start_time = pygame.time.get_ticks()

    def draw(self, surface, camera_x):
        if self.is_active:
            surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


# Монеты
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, frames, animation_speed=0.2):
        super().__init__()
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))


class FinishLine(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Например, задаём финишную линию как яркую платформу (можно заменить изображением)
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 215, 0))  # золотой цвет
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))

def load_coin_frames():
    """
    Допустим, 8 кадров в одной строке, 16x16 каждый.
    """
    frames = []
    try:
        coin_sheet = pygame.image.load(os.path.join("assets_first", "coin_sheet.png")).convert_alpha()
    except Exception as e:
        print("Ошибка загрузки coin_sheet.png:", e)
        sys.exit()

    frame_width = 16
    frame_height = 16
    num_frames = 8

    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        frame_surf = coin_sheet.subsurface(rect)
        scale_factor = 2
        frame_surf = pygame.transform.scale(frame_surf, (frame_width * scale_factor, frame_height * scale_factor))
        frames.append(frame_surf)

    return frames


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Создаём поверхность для звёздочки
        size = 8  # Размер звёздочки
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Рисуем звёздочку (4 линии)
        color = (255, 215, 0)  # Золотой цвет
        # Горизонтальная линия
        pygame.draw.line(self.image, color, (0, size // 2), (size - 1, size // 2))
        # Вертикальная линия
        pygame.draw.line(self.image, color, (size // 2, 0), (size // 2, size - 1))
        # Диагональ \
        pygame.draw.line(self.image, color, (0, 0), (size - 1, size - 1))
        # Диагональ /
        pygame.draw.line(self.image, color, (0, size - 1), (size - 1, 0))

        self.rect = self.image.get_rect(center=(x, y))
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-5, -2)
        self.lifetime = 30
        self.angle = 0  # Для вращения
        self.rotation_speed = random.uniform(-5, 5)  # Скорость вращения
        self.original_image = self.image.copy()  # Сохраняем оригинальное изображение

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.vel_y += 0.2
        self.lifetime -= 0.5

        # Вращение звёздочки
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surface, camera_x):
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y))
# ------------------------
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ УРОВНЯ
# ------------------------
platforms = None
coins = None
finish_group = None
player = None
LEVEL_WIDTH = None
level_completed = False
particles = None
current_level = None
button_font = pygame.font.SysFont(None, 36)
# ------------------------
# СОЗДАЁМ УРОВЕНЬ
# ------------------------

def init_level(level_num):
    global platforms, coins, finish_group, player, LEVEL_WIDTH, level_completed, current_level,restart_button_rect,particles
    current_level = level_num
    level_completed = False
    global level_start_time
    # В существующую функцию добавляем:
    level_start_time = time.time()

    data = level_data[level_num]
    LEVEL_WIDTH = data["LEVEL_WIDTH"]
    particles = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    finish_group = pygame.sprite.Group()
    coin_frames = load_coin_frames()
    # Пол (невидимый)
    floor = StationaryPlatform(0, 523, LEVEL_WIDTH, 50)
    floor.image.set_alpha(0)  # 0 - полностью прозрачное изображение
    platforms.add(floor)
    # Стены
    left_wall = StationaryPlatform(-10, 0, 10, HEIGHT)
    right_wall = StationaryPlatform(LEVEL_WIDTH, 0, 10, HEIGHT)
    platforms.add(left_wall)
    platforms.add(right_wall)

    # Создаем платформы из данных
    for data_item in data["platform_layout"]:
        x, y, w, h, p_type = data_item
        if p_type == "stationary":
            plat = StationaryPlatform(x, y, w, h)
        elif p_type == "moving":
            plat = MovingPlatform(x, y, w, h, x1=x - 100, x2=x + 100, speed=2)
        elif p_type == "temporary":
            plat = TemporaryPlatform(x, y, w, h, disappear_delay=3.0)
        platforms.add(plat)

    # Монеты
    for pos in data["coins_positions"]:
        cx, cy = pos
        coins.add(Coin(cx, cy,coin_frames))

    # Финишная линия
    fx, fy, fw, fh = data["finish_line"]
    finish_line = FinishLine(fx, fy, fw, fh)
    finish_line.image.set_alpha(0)
    finish_group.add(finish_line)

    # Игрок (начальная позиция)
    player = Player(50, 500)


# ------------------------
# МЕНЮ ВЫБОРА УРОВНЯ
# ------------------------
def level_selection_menu():
    menu_font = pygame.font.SysFont(None, 72)
    button_font = pygame.font.SysFont(None, 48)

    level1_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 50)
    level2_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 50)

    selecting = True
    while selecting:
        screen.fill((50, 50, 50))
        title_text = menu_font.render("Выберите уровень", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
        screen.blit(title_text, title_rect)

        pygame.draw.rect(screen, (200, 200, 200), level1_button)
        pygame.draw.rect(screen, (200, 200, 200), level2_button)

        level1_text = button_font.render("Уровень 1", True, (0, 0, 0))
        level2_text = button_font.render("Уровень 2", True, (0, 0, 0))
        screen.blit(level1_text, level1_text.get_rect(center=level1_button.center))
        screen.blit(level2_text, level2_text.get_rect(center=level2_button.center))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if level1_button.collidepoint(event.pos):
                    init_level(1)
                    selecting = False
                if level2_button.collidepoint(event.pos):
                    init_level(2)
                    selecting = False
        clock.tick(60)




# ------------------------
# ОСНОВНОЙ ЦИКЛ
# ------------------------
level_selection_menu()

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if restart_button_rect.collidepoint(event.pos):
                init_level(current_level)  # Рестарт текущего уровня

    if not level_completed:
        for plat in platforms:
            plat.update()
        old_rect = player.rect.copy()
        player.update(platforms)
        for plat in platforms:
            if isinstance(plat, TemporaryPlatform):
                if player.rect.colliderect(plat.rect) and plat.is_active:
                    plat.on_player_collide()

        coins.update()
        # Здесь можно добавить проверку сбора монет и т.д.
        if pygame.sprite.spritecollide(player, finish_group, False):
            level_completed = True

    camera_x = player.rect.centerx - WIDTH // 2
    camera_x = max(0, min(camera_x, LEVEL_WIDTH - WIDTH))

    if background_img:
        background_rect = pygame.Rect(camera_x, 0, WIDTH, HEIGHT)
        screen.blit(background_img, (0, 0), background_rect)
    else:
        screen.fill((135, 206, 235))

    for plat in platforms:
        if hasattr(plat, "is_active") and plat.is_active is False:
            continue
        plat.draw(screen, camera_x)
    collected_coins = pygame.sprite.spritecollide(player, coins, True)
    if collected_coins:
        for coin in collected_coins:
            for _ in range(7):  # 5 частиц на монету
                particles.add(Particle(coin.rect.centerx, coin.rect.centery))
        player.coins_collected += len(collected_coins)
    for coin in coins:
        coin.draw(screen, camera_x)
    for finish in finish_group:
        finish.draw(screen, camera_x)

    for particle in list(particles):
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)

        # Отрисовываем частицы
    for particle in particles:
        particle.draw(screen, camera_x)
    player.draw(screen, camera_x)

    # Счёт
    score_text = pygame.font.SysFont(None, 36).render(f"Coins: {player.coins_collected}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    # Сообщение о прохождении уровня
    if level_completed:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        win_text = pygame.font.SysFont(None, 72).render("Уровень пройден!", True, (255, 255, 255))
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(win_text, win_rect)
        pygame.display.flip()
        time.sleep(3)
        level_selection_menu()

    restart_button_rect = pygame.Rect(WIDTH - 110, 10, 100, 40)
    restart_text = button_font.render("Рестарт", True, (0, 0, 0))
    pygame.draw.rect(screen, (200, 200, 200), restart_button_rect)
    pygame.draw.rect(screen, (0, 0, 0), restart_button_rect, 2)
    text_rect = restart_text.get_rect(center=restart_button_rect.center)
    screen.blit(restart_text, text_rect)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    global_mouse_x = mouse_x + camera_x
    global_mouse_y = mouse_y
    debug_text = pygame.font.SysFont(None, 24).render(f"Mouse: ({global_mouse_x}, {global_mouse_y})", True,(255, 0, 0))
    screen.blit(debug_text, (10, HEIGHT - 30))

    current_time = time.time() - level_start_time
    time_text = pygame.font.SysFont(None, 36).render(f"Time: {int(current_time)}s", True, (0, 0, 0))
    screen.blit(time_text, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()