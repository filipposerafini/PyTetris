import random
import math
import pygame
from pygame.locals import *

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (255, 128, 255)
ORANGE = (255, 128, 0)

# Dimenstions
FIELD_WIDTH = 10
FIELD_HEIGHT = 18

ROW_OFFSET = 2
COL_OFFSET = 1

BOX_WIDTH = 6
BOX_HEIGHT = 4

PADDING = 1

FONT_SIZE = 50

# Settings
GUI_SCALE = 60
SHOW_GRID = True
FPS = 5

# Tetrominos
TETROMINOS = {

        'I': [[0, 0, 0, 0],
              [1, 1, 1, 1],
              [0, 0, 0, 0],
              [0, 0, 0, 0]],

        'J': [[1, 0, 0],
              [1, 1, 1],
              [0, 0, 0]],

        'L': [[0, 0, 1],
              [1, 1, 1],
              [0, 0 ,0]],

        'O': [[1, 1],
              [1, 1]],

        'S': [[0, 1, 1],
              [1, 1, 0],
              [0, 0, 0]],

        'T': [[0, 1, 0],
              [1, 1, 1],
              [0, 0, 0]],

        'Z': [[1, 1, 0],
              [0, 1, 1],
              [0, 0, 0]]
        }

COLORS = {
        'I': CYAN,
        'J': BLUE,
        'L': ORANGE,
        'O': YELLOW,
        'S': GREEN,
        'T': MAGENTA,
        'Z': RED
        }

KEYS = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

ROTATION_TESTS = [
        [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)]
        ]

I_ROTATION_TESTS = [
        [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)]
        ]

class Tetromino:

    def __init__(self, key=None):
        if key:
            self.key = key
        else:
            self.key = random.choice(KEYS)
        self.shape = TETROMINOS[self.key]
        self.color = COLORS[self.key]
        self.top = 0
        if self.key == 'O':
            self.left = 5
        else:
            self.left = 4
        self.orientation = 0

    def check_collisions(self, placed, new_pos, test_shape=None):
        if test_shape:
            shape = test_shape
        else:
            shape = self.shape
        x, y = new_pos
        left = self.left + x
        top = self.top + y
        for r in range(len(self.shape)):
            for c in range(len(self.shape)):
                if placed[top + r][left + c] and shape[r][c]:
                    return False
        return True

    def shift(self, placed, delta):
        if self.check_collisions(placed, (delta, 0)):
            self.left += delta

    def reset(self):
        return Tetromino(key=self.key)

    def rotate(self, placed):
        new_shape = list(zip(*self.shape[::-1]))

        tests = I_ROTATION_TESTS if self.key == 'I' else ROTATION_TESTS

        for test in tests[self.orientation]:
            if self.check_collisions(placed, test, test_shape=new_shape):
                left, top = test
                self.top += top
                self.left += left
                self.shape = new_shape
                self.orientation = (self.orientation + 1) % 4
                break
    
    def down(self, placed):
        for i in range(1, FIELD_HEIGHT):
            if not self.check_collisions(placed, (0, i)):
                self.top += (i - 1)
                return

    def draw(self, surface, cell_size, prev=False, hold=False):
        col = PADDING + self.left - COL_OFFSET
        row = PADDING + self.top - ROW_OFFSET
        if self.key == 'I':
            col_offset = 0
        elif self.key == 'O':
            col_offset = 1
        else:
            col_offset = 0.5
        row_offset = 0.5 if self.key == 'I' else 0
        if prev:
            col = 3 * PADDING + FIELD_WIDTH + col_offset
            row = 4 * PADDING - row_offset
        if hold:
            col = 3 * PADDING + FIELD_WIDTH + col_offset
            row = FIELD_HEIGHT - 2 * PADDING - row_offset
        for r in range(len(self.shape)):
            for c in range(len(self.shape)):
                if self.shape[r][c] == 1:
                    rect = pygame.Rect((col + c) * cell_size, (row + r) * cell_size, cell_size, cell_size)
                    pygame.draw.rect(surface, self.color, rect)

class Game:

    def __init__(self, surface, cell_size):

        self.screen = surface
        self.cell_size = cell_size
        
        font = pygame.font.Font('font.ttf', FONT_SIZE)

        self.field_box = pygame.Rect(PADDING * cell_size,
                                     PADDING * cell_size,
                                     FIELD_WIDTH * cell_size,
                                     FIELD_HEIGHT * cell_size)

        next_text = font.render('NEXT', True, WHITE)
        next_rect = next_text.get_rect()
        self.next_box = pygame.Rect((FIELD_WIDTH + 2 * PADDING) * cell_size,
                                    PADDING * cell_size + next_rect.height,
                                    BOX_WIDTH * cell_size,
                                    BOX_HEIGHT * cell_size)
        next_rect.midbottom = ((2 * PADDING + FIELD_WIDTH) * cell_size + self.next_box.width / 2, self.next_box.top - 0.3 * cell_size)

        self.screen.blit(next_text, next_rect)
        pygame.draw.rect(self.screen, WHITE, self.next_box, width=3)

        hold_text = font.render('HOLD', True, WHITE)
        hold_rect = hold_text.get_rect()
        self.hold_box = pygame.Rect((FIELD_WIDTH + 2 * PADDING) * cell_size,
                                    self.screen.get_height() - (PADDING + BOX_HEIGHT) * cell_size,
                                    BOX_WIDTH * cell_size,
                                    BOX_HEIGHT * cell_size)
        hold_rect.midbottom = ((2 * PADDING + FIELD_WIDTH) * cell_size + self.hold_box.width / 2, self.hold_box.top - 0.3 * cell_size)

        self.screen.blit(hold_text, hold_rect)
        pygame.draw.rect(self.screen, WHITE, self.hold_box, width=3)

        self.next_tetromino = Tetromino()
        self.next_tetromino.draw(self.screen, cell_size, prev=True)

        self.hold_tetromino = None
        self.hold = False

        pygame.display.flip()

        self.placed = [['' for c in range(FIELD_WIDTH + COL_OFFSET + 1)] for r in range(FIELD_HEIGHT + ROW_OFFSET + 2)]

        for r in range(FIELD_HEIGHT + ROW_OFFSET + 1):
            for c in range(FIELD_WIDTH + COL_OFFSET + 1):
                if r == (FIELD_HEIGHT + ROW_OFFSET) or c == 0 or c == (FIELD_WIDTH + COL_OFFSET):
                    self.placed[r][c] = 'W'

    def print(self):
        for r in range(FIELD_HEIGHT + ROW_OFFSET + 1):
            for c in range(FIELD_WIDTH + COL_OFFSET + 1):
                if self.placed[r][c]:
                    print(self.placed[r][c], end=' ')
                else:
                    print(' ', end=' ')
            print()
        print('\n')

    def next_piece(self):
        tetromino = self.next_tetromino
        self.next_tetromino = Tetromino()

        self.screen.fill(BLACK, rect=self.next_box)
        self.next_tetromino.draw(self.screen, self.cell_size, prev=True)
        pygame.draw.rect(self.screen, WHITE, self.next_box, width=3)
        pygame.display.update(self.next_box)

        return tetromino

    def hold_piece(self, tetromino):
        if not self.hold:
            self.hold = True
            if self.hold_tetromino:
                new = self.hold_tetromino
            else:
                new = self.next_piece()

            self.hold_tetromino = tetromino.reset()

            self.screen.fill(BLACK, rect=self.hold_box)
            self.hold_tetromino.draw(self.screen, self.cell_size, hold=True)
            pygame.draw.rect(self.screen, WHITE, self.hold_box, width=3)
            pygame.display.update(self.hold_box)
            
            return new
        else:
            return tetromino

    def landed(self, tetromino):
        if tetromino.check_collisions(self.placed, (0, 1)):
            tetromino.top += 1
            return False
        else:
            for r in range(len(tetromino.shape)):
                for c in range(len(tetromino.shape)):
                    if tetromino.shape[r][c]:
                        self.placed[tetromino.top + r][tetromino.left + c] = tetromino.key
            self.print()
            self.hold = False
            return True

    def clear_lines(self):
        cleared = []
        for r in range(ROW_OFFSET, FIELD_HEIGHT + ROW_OFFSET):
            if all(self.placed[r]):
                cleared.append(r)

        for i in sorted(cleared, reverse=True):
            del self.placed[i]

        for _ in cleared:
            self.placed.insert(0, ['W'] + FIELD_WIDTH * [''] + ['W'])

        return len(cleared)

    def draw(self, tetromino):

        self.screen.fill(BLACK, rect=self.field_box)

        for c in range(1, FIELD_WIDTH + COL_OFFSET):
            for r in range(2, FIELD_HEIGHT + ROW_OFFSET):
                if self.placed[r][c]:
                    rect = pygame.Rect((PADDING + c - COL_OFFSET) * self.cell_size,
                                       (PADDING + r - ROW_OFFSET) * self.cell_size,
                                       self.cell_size,
                                       self.cell_size)
                    pygame.draw.rect(self.screen, COLORS[self.placed[r][c]], rect)

        tetromino.draw(self.screen, self.cell_size)

        if SHOW_GRID:
            for r in range(1, FIELD_HEIGHT + 1):
                pygame.draw.line(self.screen,
                                 GRAY,
                                 (PADDING * self.cell_size, (PADDING + r) * self.cell_size),
                                 ((PADDING + FIELD_WIDTH) * self.cell_size, (PADDING + r) * self.cell_size))

            for c in range(1, FIELD_WIDTH + 1):
                pygame.draw.line(self.screen,
                                 GRAY, 
                                 ((PADDING + c) * self.cell_size, PADDING * self.cell_size),
                                 ((PADDING + c) * self.cell_size, (PADDING + FIELD_HEIGHT) * self.cell_size))

        pygame.draw.rect(self.screen, WHITE, self.field_box, width=3)

        pygame.display.update(self.field_box)

def init_screen(caption, scale=GUI_SCALE):
    pygame.init()
    pygame.display.set_caption(caption)
    # icon = pygame.image.load('resources/icon.png')
    # pygame.display.set_icon(icon)

    pygame.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])

    cell_size = int(pygame.display.Info().current_w / scale)
    width = FIELD_WIDTH * cell_size + 3 * PADDING * cell_size + BOX_WIDTH * cell_size
    height = FIELD_HEIGHT * cell_size + 2 * PADDING * cell_size
    screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)

    screen.fill(BLACK)

    return cell_size, screen

if __name__ == '__main__':

    cell_size, screen = init_screen('Tetris')

    game = Game(screen, cell_size)
    tetromino = Tetromino()

    timer_event = pygame.USEREVENT + 1
    update_delay = 150
    pygame.time.set_timer(timer_event, update_delay)

    running = True

    while running:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pass

                elif event.key == pygame.K_SPACE:
                    pass

                elif event.key == pygame.K_UP:
                    tetromino.rotate(game.placed)

                elif event.key == pygame.K_LEFT:
                    tetromino.shift(game.placed, -1)

                elif event.key == pygame.K_RIGHT:
                    tetromino.shift(game.placed, 1)

                elif event.key == pygame.K_DOWN:
                    tetromino.down(game.placed)
                    pass

                elif event.key == pygame.K_h:
                    tetromino = game.hold_piece(tetromino)

                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == timer_event:
                if game.landed(tetromino):
                    game.clear_lines()
                    tetromino = game.next_piece()

            else:
                continue

        game.draw(tetromino)

    # Quit
    pygame.quit()
