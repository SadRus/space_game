import asyncio
import curses
import random
import time

from curses_tools import draw_frame, get_frame_size, read_controls
from itertools import cycle

ROCKET_ROWS_SPEED = 1
ROCKET_COLUMNS_SPEED = 1
STARS_COUNT_MIN = 80
STARS_COUNT_MAX = 130
STAR_SYMBOLS = '+*.:'
STARS_BORDER_OFFSET = 3
TIC_TIMEOUT = 0.1
STARS_BLINK_TIC_OFFSET = (5, 15)
SPACESHIP_ANIMATION_TIC_OFFSET = 2
BORDER_OFFSET = 1


async def blink(canvas, row, column, symbol, tic_offset):
    while True:
        for _ in range(tic_offset):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


def animate_stars(canvas, rows, columns, star_symbols):
    coroutines = []
    for _ in range(random.randint(STARS_COUNT_MIN, STARS_COUNT_MAX)):
        tic_offset = random.randint(*STARS_BLINK_TIC_OFFSET)
        coroutines.append(blink(
            canvas,
            row=random.randint(STARS_BORDER_OFFSET, rows - STARS_BORDER_OFFSET),
            column=random.randint(STARS_BORDER_OFFSET, columns - STARS_BORDER_OFFSET),
            symbol=random.choice(star_symbols),
            tic_offset=tic_offset,
        ))
    return coroutines


async def animate_spaceship(canvas, start_row, start_column, rocket_frames):
    canvas_min_row, canvas_min_column = canvas.getbegyx()
    canvas_max_row, canvas_max_column = canvas.getmaxyx()

    rocket_row, rocket_column = start_row, start_column
    rocket_frame_rows, rocket_frame_columns = get_frame_size(rocket_frames[0])

    rows_speed = columns_speed = 0
    for rocket_frame in cycle(rocket_frames):
        for _ in range(SPACESHIP_ANIMATION_TIC_OFFSET):
            rows_speed, columns_speed, _ = read_controls(canvas, ROCKET_ROWS_SPEED, ROCKET_COLUMNS_SPEED)
            rocket_row += rows_speed
            rocket_column += columns_speed
            rocket_row = min(
                max(canvas_min_row + BORDER_OFFSET, rocket_row),
                canvas_max_row - rocket_frame_rows - BORDER_OFFSET,
            )
            rocket_column = min(
                max(canvas_min_column + BORDER_OFFSET, rocket_column),
                canvas_max_column - rocket_frame_columns - BORDER_OFFSET,
            )

            draw_frame(canvas, round(rocket_row), round(rocket_column), rocket_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, round(rocket_row), round(rocket_column), rocket_frame, negative=True)



def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    with open('./animations/rocket_frame_1.txt') as file:
        rocket_frame_1 = file.read()

    with open('./animations/rocket_frame_2.txt') as file:
        rocket_frame_2 = file.read()

    canvas_rows, canvas_columns = canvas.getmaxyx()
    rocket_frames = [rocket_frame_1, rocket_frame_2]

    animate_stars_coroutines = animate_stars(canvas, canvas_rows, canvas_columns, STAR_SYMBOLS)
    coroutines = [
        *animate_stars_coroutines,
        animate_spaceship(canvas, canvas_rows//2, canvas_columns//2, rocket_frames),
    ]
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
        if len(coroutines) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
