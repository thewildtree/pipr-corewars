import os
import glob
import argparse
from typing import List
import pygame
from corewars.mars import MARS
from corewars.core import CoreWarrior


CELLS_PER_LINE = 100
LINES = 80
CELL_SIZE = 10
SPACING = 2
SIDEBAR_WIDTH = 350

WINDOW_WIDTH = SPACING + (CELLS_PER_LINE * (CELL_SIZE + SPACING)) + SIDEBAR_WIDTH
WINDOW_HEIGHT = SPACING + (LINES * (CELL_SIZE + SPACING))
SIDEBAR_START = WINDOW_WIDTH - SIDEBAR_WIDTH
INFO_MARGIN = 20
ENTRY_SPACING = (WINDOW_WIDTH - 200) // 15


COLOURS = [
    (55, 183, 106), # green
    (75, 160, 227), # blue
    (255, 159, 16), # orange
    (206, 55, 70),  # red
    (240, 76, 169)  # dark blue
]

BASE_CELL_COLOUR = (30, 30, 30)
SIDEBAR_COLOUR = (20, 20, 20)
FONT_SIZE = 20


def main():
    print(pygame.font.get_fonts())
    parser = argparse.ArgumentParser(description='Core Wars')
    parser.add_argument('--cycles', '-c', dest='cycles', type=int, nargs='?',
                        default=80000, help='Max sim. cycles before round end')
    parser.add_argument('--warriors', type=str, default='warriors',
                        help='Name of the folder containing warrior files')
    args = parser.parse_args()
    # laod warriors
    warrior_files = glob.glob(os.path.join(os.getcwd(), "warriors", "*.red"))
    if not warrior_files:
        print('No warrior files found. Aborting...')
        return
    pygame.init()
    # 1202px horizontal, 962px needed (10px per square, 2px spacing)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    warriors_data = [open(file).readlines() for file in warrior_files]
    run_simulation(screen, warriors_data, args.cycles)


def run_simulation(screen, warriors_data: List[List[str]], max_cycles: int):
    # initialize the simulator and load up provided warriors
    mars = MARS()
    mars.load_warriors(warriors_data)
    mars.core.assign_colors(COLOURS)
    # initial stats display
    screen.fill((0, 0, 0))
    sidebar = pygame.Surface((SIDEBAR_WIDTH, WINDOW_HEIGHT))
    sidebar.fill(SIDEBAR_COLOUR)
    screen.blit(sidebar, (SIDEBAR_START, 0))
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
    game_ended = False
    run_again = False
    cycles = 1
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    run_again = True
                    loop = False
        if game_ended:
            continue
        # change previous cursor to warrior's colour
        display_cursor(screen, mars)
        # save current execution pointer to prevent erasing it afterwards
        pointer = mars.core.current_warrior.current_pointer
        # save current warrior's colour for later use
        color = mars.core.current_warrior.color
        # run simulation cycle and save accessed cells
        addresses = mars.cycle()
        # display sidebar content
        sidebar.fill((20, 20, 20))
        write_text(sidebar, f'CYCLE {cycles + 1}', INFO_MARGIN, 20)
        for i, warrior in enumerate(mars.core.warriors + mars.core.dead_warriors):
            print_warrior_info(sidebar, i, warrior)
        # one warrior left = win
        if mars.core.warriors_count == 1:
            game_ended = True
            write_text(sidebar, f'{mars.core.current_warrior.name.upper()} WINS!', INFO_MARGIN, 100, 'Gold')
        # max cycles passed = tie
        elif cycles + 1 >= max_cycles:
            game_ended = True
            write_text(sidebar, 'GAME OVER - NO WINNER.', INFO_MARGIN, 50, 'Red')
        write_text(sidebar, 'CTRL-R to reset', INFO_MARGIN, WINDOW_HEIGHT - 30)
        screen.blit(sidebar, (SIDEBAR_START, 0))
        # cells accessed / written to during this cycle
        if pointer in addresses:
            addresses.remove(pointer)
        for address in addresses:
            cell = create_written_cell(color)
            pos = get_position(address, mars.core.size)
            screen.blit(cell, pos)
        # show current warrior's pointer (blink white)
        display_cursor(screen, mars, True)
        pygame.display.flip()
        cycles += 1
    if run_again:
        run_simulation(screen, warriors_data, max_cycles)


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


def print_warrior_info(sidebar, pos: int, warrior: CoreWarrior):
    v_margin = 200 + (pos * ENTRY_SPACING)
    warrior_entry = pygame.Surface((SIDEBAR_WIDTH, ENTRY_SPACING))
    warrior_entry.fill(SIDEBAR_COLOUR)
    square = pygame.Surface((20, 20))
    square.fill(warrior.color)
    warrior_entry.blit(square, (0, 5))
    write_text(warrior_entry, warrior.name, 30, 5)
    if len(warrior) > 0:
        write_text(warrior_entry, f'processes: {len(warrior)}', 30, 30)
    else:
        write_text(warrior_entry, 'processes: 0 (dead)', 30, 30)
    sidebar.blit(warrior_entry, (INFO_MARGIN, v_margin))


def write_text(screen, text: str, x: int, y: int, color='White'):
    font = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)
    text = font.render(text, True, pygame.Color(color))
    screen.blit(text, (x, y))


def get_position(address: int, core_size):
    # addresses might be passed here before Core itself normalizes them
    address = address % core_size
    y = SPACING + (address // CELLS_PER_LINE) * (CELL_SIZE + SPACING)
    x = SPACING + (address % CELLS_PER_LINE) * (CELL_SIZE + SPACING)
    return (x, y)


if __name__ == '__main__':
    main()
