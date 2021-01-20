import os
import glob
import pygame
from typing import List
from corewars.mars import MARS

CELLS_PER_LINE = 100
LINES = 80
CELL_SIZE = 10
SPACING = 2
SIDEBAR_WIDTH = 350

WINDOW_WIDTH = SPACING + (CELLS_PER_LINE * (CELL_SIZE + SPACING)) + SIDEBAR_WIDTH
WINDOW_HEIGHT = SPACING + (LINES * (CELL_SIZE + SPACING))

COLOURS = [
    (55, 183, 106), # green
    (75, 160, 227), # blue
    (255, 159, 16), # orange
    (206, 55, 70),  # red
    (75, 128, 159)  # dark blue
]

BASE_CELL_COLOUR = (30, 30, 30)


def main():
    # laod warriors
    warrior_files = glob.glob(os.path.join(os.getcwd(), "warriors", "*.red"))
    if not warrior_files:
        print('No warrior files found. Aborting...')
        return
    pygame.init()
    # 1202px horizontal, 962px needed (10px per square, 2px spacing)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    warriors_data = [open(file).readlines() for file in warrior_files]
    run_simulation(screen, warriors_data)


def run_simulation(screen, warriors_data: List[List[str]]):
    # initialize the simulator and load up provided warriors
    mars = MARS()
    mars.load_warriors(warriors_data)
    mars.core.assign_colors(COLOURS)
    # initial stats display
    screen.fill((0, 0, 0))
    pygame.draw.line(
        screen,
        (255, 255, 255),
        (WINDOW_WIDTH - SIDEBAR_WIDTH, 0),
        (WINDOW_WIDTH - SIDEBAR_WIDTH, WINDOW_HEIGHT)
    )
    # initial cell display
    for i, _ in enumerate(mars.core):
        cell = create_cursor_cell(BASE_CELL_COLOUR)
        pos = get_position(i, mars.core.size)
        screen.blit(cell, pos)
    # initial cursor display
    display_cursor(screen, mars)
    pygame.display.flip()
    # main game loop
    loop = True
    run_again = False
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    run_again = True
                    loop = False
        # change previous cursor to warrior's colour
        display_cursor(screen, mars)
        # run one simulation cycle
        addresses = mars.cycle()
        # show current warrior's pointer (blink white)
        display_cursor(screen, mars, True)
        # cells accessed / written to during this cycle
        color = mars.core.current_warrior.color
        for address in addresses:
            cell = create_written_cell(color)
            pos = get_position(address, mars.core.size)
            screen.blit(cell, pos)
        pygame.display.flip()
    if run_again:
        run_simulation(screen, warriors_data)


def display_cursor(screen, mars: MARS, white=False):
    cursor = mars.core.current_warrior.current_pointer
    color = (255, 255, 255) if white else mars.core.current_warrior.color
    cell = create_cursor_cell(color)
    pos = get_position(cursor, mars.core.size)
    screen.blit(cell, pos)


def create_cursor_cell(color):
    cell = pygame.Surface((CELL_SIZE, CELL_SIZE))
    cell.fill(color)
    return cell


def create_written_cell(color):
    cell = pygame.Surface((CELL_SIZE, CELL_SIZE))
    pygame.draw.aaline(cell, color, (0, 0), (CELL_SIZE, CELL_SIZE))
    pygame.draw.aaline(cell, color, (0, CELL_SIZE), (CELL_SIZE, 0))
    return cell


def get_position(address: int, core_size):
    # addresses might be passed here before Core itself normalizes them
    address = address % core_size
    y = SPACING + (address // CELLS_PER_LINE) * (CELL_SIZE + SPACING)
    x = SPACING + (address % CELLS_PER_LINE) * (CELL_SIZE + SPACING)
    return (x, y)


if __name__ == '__main__':
    main()
