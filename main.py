import asyncio
import curses
import random
import time

from curses_tools import draw_frame, get_frame_size, read_controls
from itertools import cycle

ROCKET_SPEED = 1
STARS_COUNT_MIN = 80
STARS_COUNT_MAX = 130
STAR_SYMBOLS = '+*.:'
TIC_TIMEOUT = 0.1


async def blink(canvas, row, column, symbol):
    while True:
        for _ in range(random.randint(5, 15)):
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
        coroutines.append(blink(
            canvas,
            row=random.randint(5, rows - 5),
            column=random.randint(5, columns - 5),
            symbol=random.choice(star_symbols),
        ))
    return coroutines


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, start_row, start_column, rocket_frames):
    row, column = start_row, start_column

    # rows, columns = canvas.getmaxyx()
    # max_row, max_column = rows - 1, columns - 1
    # rocket_frame_size = get_frame_size(rocket_frames[0])

    row_delta = column_delta = 0
    # while 0 < row < max_row and 0 < column < max_column:
    for rocket_frame in cycle(rocket_frames):
        row_delta, column_delta, _ = read_controls(canvas)
        row += row_delta * ROCKET_SPEED
        column += column_delta * ROCKET_SPEED

        draw_frame(canvas, round(row), round(column), rocket_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, round(row), round(column), rocket_frame, negative=True)


def draw(canvas) -> None:
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)

    with open('./animations/rocket_frame_1.txt') as file:
        rocket_frame_1 = file.read()

    with open('./animations/rocket_frame_2.txt') as file:
        rocket_frame_2 = file.read()

    rows, columns = canvas.getmaxyx()
    rocket_frames = [rocket_frame_1, rocket_frame_2]

    animate_stars_coroutines = animate_stars(canvas, rows, columns, STAR_SYMBOLS)
    coroutines = [
        *animate_stars_coroutines,
        animate_spaceship(canvas, rows//2, columns//2, rocket_frames),
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
