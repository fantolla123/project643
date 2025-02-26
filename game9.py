import pygame
import random
import sys
import os
# Инициализация Pygame
pygame.init()

# Константы
WINDOW_SIZE = 800
GRID_SIZE = 8
BLOCK_SIZE = 70
GRID_OFFSET_X = (WINDOW_SIZE - GRID_SIZE * BLOCK_SIZE) // 2
GRID_OFFSET_Y = 50
GEM_IMAGES = None
# Цвета
COLORS = {
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'PURPLE': (255, 0, 255),
    'CYAN': (0, 255, 255)
}


def load_gem_images(spritesheet_path):
    try:
        spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

        # Определяем размер одного кристалла в спрайтшите
        gem_width = spritesheet.get_width() // 5  # 5 кристаллов в ряду
        gem_height = spritesheet.get_height() // 4  # 4 ряда (цвета)

        images = {}
        colors = ['blue', 'pink', 'yellow', 'green']
        shapes = ['diamond', 'pyramid', 'hexagon', 'circle', 'heart']

        for row, color in enumerate(colors):
            images[color] = {}
            for col, shape in enumerate(shapes):
                # Вырезаем нужный кристалл из спрайтшита
                surface = pygame.Surface((gem_width, gem_height), pygame.SRCALPHA)
                rect = pygame.Rect(col * gem_width, row * gem_height, gem_width, gem_height)
                surface.blit(spritesheet, (0, 0), rect)

                # Масштабируем под размер блока
                images[color][shape] = pygame.transform.scale(surface, (BLOCK_SIZE - 4, BLOCK_SIZE - 4))

        return images
    except Exception as e:
        print(f"Ошибка загрузки спрайтшита: {e}")
        return None



class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visual_x = x
        self.visual_y = y
        # Случайный выбор цвета и формы
        self.color = random.choice(['blue', 'pink', 'yellow', 'green'])
        self.shape = random.choice(['diamond', 'pyramid', 'hexagon', 'circle', 'heart'])
        self.image = GEM_IMAGES[self.color][self.shape]
        self.selected = False
        self.fall_speed = 0
        self.is_falling = False
        self.is_moving = False
        self.target_x = x
        self.target_y = y
        self.move_speed = 0.2
        self.rotation = 0
        self.scale = 1.0

    def get_color_name(self, color):
        # Преобразуем RGB в название цвета
        color_map = {
            COLORS['RED']: 'red',
            COLORS['BLUE']: 'blue',
            COLORS['GREEN']: 'green',
            COLORS['YELLOW']: 'yellow',
            COLORS['PURPLE']: 'purple',
            COLORS['CYAN']: 'cyan'
        }
        return color_map[color]

    def update(self):
        # Анимация перемещения
        if self.is_moving:
            dx = self.target_x - self.visual_x
            dy = self.target_y - self.visual_y

            # Плавное перемещение к цели
            if abs(dx) > 0.01:
                self.visual_x += dx * self.move_speed
            else:
                self.visual_x = self.target_x

            if abs(dy) > 0.01:
                self.visual_y += dy * self.move_speed
            else:
                self.visual_y = self.target_y

            # Проверяем, достигли ли целевой позиции
            if abs(self.visual_x - self.target_x) < 0.01 and abs(self.visual_y - self.target_y) < 0.01:
                self.visual_x = self.target_x
                self.visual_y = self.target_y
                self.is_moving = False

        # Анимация падения
        if self.is_falling:
            self.fall_speed = min(self.fall_speed + 0.5, 15)
            self.visual_y += self.fall_speed

            if self.visual_y >= self.target_y:
                self.visual_y = self.target_y
                self.is_falling = False

    def draw(self, screen):
        if self.image:
            # Позиция для отрисовки
            x = GRID_OFFSET_X + self.visual_x * BLOCK_SIZE + 2
            y = GRID_OFFSET_Y + self.visual_y * BLOCK_SIZE + 2

            # Если блок выбран, рисуем подсветку
            if self.selected:
                glow_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (255, 255, 200, 100),
                                 (0, 0, BLOCK_SIZE, BLOCK_SIZE), border_radius=10)
                screen.blit(glow_surf, (x - 2, y - 2))

            # Рисуем тень
            shadow_offset = 2
            shadow_surf = pygame.Surface((BLOCK_SIZE - 4, BLOCK_SIZE - 4), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 50))
            screen.blit(shadow_surf, (x + shadow_offset, y + shadow_offset))

            # Рисуем сам кристалл
            screen.blit(self.image, (x, y))

class GameBoard:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected_block = None
        self.fill_board()

    def fill_board(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                color = random.choice(list(COLORS.values()))
                self.grid[y][x] = Block(x, y)

    def draw(self, screen):
        # Рисуем фон игрового поля
        board_rect = pygame.Rect(
            GRID_OFFSET_X - 5,
            GRID_OFFSET_Y - 5,
            GRID_SIZE * BLOCK_SIZE + 10,
            GRID_SIZE * BLOCK_SIZE + 10
        )
        pygame.draw.rect(screen, (150, 150, 150), board_rect)

        # Рисуем блоки
        for row in self.grid:
            for block in row:
                if block:
                    block.draw(screen)

    def get_block_at_pixel(self, pos_x, pos_y):
        # Конвертируем координаты экрана в координаты сетки
        grid_x = (pos_x - GRID_OFFSET_X) // BLOCK_SIZE
        grid_y = (pos_y - GRID_OFFSET_Y) // BLOCK_SIZE

        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            return self.grid[grid_y][grid_x]
        return None

    def handle_click(self, pos):
        clicked_block = self.get_block_at_pixel(*pos)
        if not clicked_block:
            return

        if not self.selected_block:
            # Первый выбранный блок
            clicked_block.selected = True
            self.selected_block = clicked_block
        else:
            # Второй выбранный блок
            if self.are_blocks_adjacent(self.selected_block, clicked_block):
                self.swap_blocks(self.selected_block, clicked_block)

            # Снимаем выделение
            self.selected_block.selected = False
            self.selected_block = None

    def are_blocks_adjacent(self, block1, block2):
        return (abs(block1.x - block2.x) == 1 and block1.y == block2.y) or \
            (abs(block1.y - block2.y) == 1 and block1.x == block2.x)

    def swap_blocks(self, block1, block2):
        # Запоминаем старые позиции
        old_x1, old_y1 = block1.x, block1.y
        old_x2, old_y2 = block2.x, block2.y

        # Меняем координаты блоков
        block1.x, block2.x = block2.x, block1.x
        block1.y, block2.y = block2.y, block1.y

        # Устанавливаем целевые позиции для анимации
        block1.target_x = block1.x
        block1.target_y = block1.y
        block2.target_x = block2.x
        block2.target_y = block2.y

        # Запускаем анимацию
        block1.is_moving = True
        block2.is_moving = True

        # Обновляем сетку
        self.grid[block1.y][block1.x] = block1
        self.grid[block2.y][block2.x] = block2

        # Проверяем, появились ли совпадения
        matches = self.check_matches()
        if not matches:
            # Если совпадений нет, возвращаем блоки обратно
            block1.x, block1.y = old_x1, old_y1
            block2.x, block2.y = old_x2, old_y2
            block1.target_x = old_x1
            block1.target_y = old_y1
            block2.target_x = old_x2
            block2.target_y = old_y2
            self.grid[block1.y][block1.x] = block1
            self.grid[block2.y][block2.x] = block2
            return False

        return True
    def check_matches(self):
        """Проверяет все возможные совпадения на поле"""
        matches = set()  # Используем set чтобы избежать дубликатов

        # Проверяем горизонтальные совпадения
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE - 2):
                if self.grid[y][x] and self.grid[y][x + 1] and self.grid[y][x + 2]:  # Проверяем что блоки существуют
                    if (self.grid[y][x].color == self.grid[y][x + 1].color == self.grid[y][x + 2].color):
                        matches.add(self.grid[y][x])
                        matches.add(self.grid[y][x + 1])
                        matches.add(self.grid[y][x + 2])

        # Проверяем вертикальные совпадения
        for y in range(GRID_SIZE - 2):
            for x in range(GRID_SIZE):
                if self.grid[y][x] and self.grid[y + 1][x] and self.grid[y + 2][x]:
                    if (self.grid[y][x].color == self.grid[y + 1][x].color == self.grid[y + 2][x].color):
                        matches.add(self.grid[y][x])
                        matches.add(self.grid[y + 1][x])
                        matches.add(self.grid[y + 2][x])

        return matches

    def remove_matches(self, matches):
        """Удаляет совпавшие блоки и помечает блоки для падения"""
        for block in matches:
            self.grid[block.y][block.x] = None

    def apply_gravity(self):
        """Обрабатывает падение блоков"""
        falling_blocks = []

        # Проверяем каждую колонку снизу вверх
        for x in range(GRID_SIZE):
            empty_y = None  # Позиция для падения

            # Идём снизу вверх
            for y in range(GRID_SIZE - 1, -1, -1):
                if self.grid[y][x] is None and empty_y is None:
                    empty_y = y
                elif self.grid[y][x] is not None and empty_y is not None:
                    # Нашли блок, который должен упасть
                    block = self.grid[y][x]
                    self.grid[y][x] = None
                    block.target_y = empty_y
                    block.is_falling = True
                    block.fall_speed = 0
                    falling_blocks.append(block)
                    empty_y -= 1

        return falling_blocks

    def fill_empty_spaces(self):
        """Заполняет пустые места сверху новыми блоками"""
        new_blocks = []

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if self.grid[y][x] is None:
                    color = random.choice(list(COLORS.values()))
                    new_block = Block(x, -1)  # Создаём блок над полем
                    new_block.target_y = y
                    new_block.is_falling = True
                    new_block.fall_speed = 0
                    new_blocks.append(new_block)
                    self.grid[y][x] = new_block

        return new_blocks


def main():
    global GEM_IMAGES
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Match-3 Game")
    GEM_IMAGES = load_gem_images(os.path.join('assets', 'gems_spritesheet.png'))
    clock = pygame.time.Clock()
    board = GameBoard()
    falling_blocks = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not falling_blocks:
                # Проверяем, что ни один блок не анимируется
                if not any(block.is_moving for row in board.grid for block in row if block):
                    if board.handle_click(event.pos):
                        matches = board.check_matches()
                        if matches:
                            board.remove_matches(matches)
                            falling_blocks.extend(board.apply_gravity())
                            falling_blocks.extend(board.fill_empty_spaces())

        # Обновляем все блоки
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if board.grid[y][x]:
                    board.grid[y][x].update()

        # Проверяем новые совпадения после остановки всех анимаций
        if not falling_blocks and not any(block.is_moving for row in board.grid for block in row if block):
            matches = board.check_matches()
            if matches:
                board.remove_matches(matches)
                falling_blocks.extend(board.apply_gravity())
                falling_blocks.extend(board.fill_empty_spaces())

        # Отрисовка
        screen.fill((200, 200, 200))
        board.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()