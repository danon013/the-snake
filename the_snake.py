from random import randint

import pygame as pg

pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER_X, SCREEN_CENTER_Y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
SCREEN_CENTER = (SCREEN_CENTER_X, SCREEN_CENTER_Y)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет камня
STONE_COLOR = (100, 100, 100)

# Цвет змейки
SNAKE_COLOR = (130, 70, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject():
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position, body_color):
        self.position = position or (SCREEN_CENTER_X, SCREEN_CENTER_Y)
        self.body_color = body_color

    def draw_cell(self, position=None):
        """Повторяющийся код для отрисовки ячейки."""
        position = position or self.position
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Метод для отрисовки объектов.

        По умолчанию ничего не делает.
        Дочерние классы переопределят его
        и реализуют собственную отрисовку объектов на экране.
        """
        raise NotImplementedError('Метод будет реализован в дочерних классах')


class Apple(GameObject):
    """Дочерний класс.

    Отвечает за появление яблока в рандомном месте и его отрисовку.
    """

    def __init__(self, body_color, occupied_positions=(SCREEN_CENTER)):
        super().__init__(position=(0, 0), body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Метод, отвечающий за появление яблока в случайном месте."""
        while True:
            pos_x = randint(0, ((SCREEN_WIDTH // GRID_SIZE) - 1))
            pos_y = randint(0, ((SCREEN_HEIGHT // GRID_SIZE) - 1))
            self.position = (pos_x * GRID_SIZE, pos_y * GRID_SIZE)

            if self.position not in occupied_positions:
                break

    def draw(self):
        """Метод отвечающий за отрисовку яблока."""
        self.draw_cell()


class Snake(GameObject):
    """Дочерний класс.

    Отвечает за хранение сегментов змейки, движение, изменение направления,
    рост после съеденного яблока, проверку столкновений,
    отрисовку змейки на экране.
    """

    def __init__(self, body_color):
        super().__init__(position=(SCREEN_CENTER), body_color=body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Этот метод возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Отвечает за обновление координат всех сегментов змейки.

        Получает текущую позицию головы через get_head_position(),
        вычисляет новую позицию головы и добавляет ее
        в начало списка positions, сохраняет последний сегмент в атрибут last
        удаляет хвостовой сегмент, если длина списка превышает значение length.
        """
        head_x, head_y = self.get_head_position()
        n_head_x, n_head_y = self.direction

        new_head_x = head_x + n_head_x * GRID_SIZE
        new_head_y = head_y + n_head_y * GRID_SIZE

        new_head_x = new_head_x % SCREEN_WIDTH
        new_head_y = new_head_y % SCREEN_HEIGHT

        self.positions.insert(0, (new_head_x, new_head_y))

        if len(self.positions) > self.length:
            self.last = self.positions[-1]
            self.positions.pop()

    def reset(self):
        """Метод возвращает змейку в изначальное состояние."""
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет текущее направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отвечает за отрисовку всех сегментов змейки."""
        for position in self.positions[:-1]:
            self.draw_cell(position)

        # Отрисовка головы змейки
        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object):
    """Используется для управления змейкой с клавиатуры."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Управляет игровым циклом.

    Здесь обрабатывается ввод через handle_keys(), проверяется
    столкновение с яблоком, змейки с собой и с камнем.
    """
    # Тут нужно создать экземпляры классов.
    snake = Snake(body_color=SNAKE_COLOR)
    apple = Apple(
        body_color=APPLE_COLOR,
        occupied_positions=snake.positions
    )
    stone = Apple(
        body_color=STONE_COLOR,
        occupied_positions=(snake.positions, apple.position)
    )

    while True:
        # Тут опишите основную логику игры.
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(
                occupied_positions=(snake.positions, stone.position)
            )

        elif snake.get_head_position() == stone.position:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            stone.randomize_position(
                occupied_positions=(snake.positions, apple.position)
            )

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        stone.draw()

        pg.display.update()
        clock.tick(SPEED)

    pg.quit()


if __name__ == '__main__':
    main()
