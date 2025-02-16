import asyncio
import curses
import random
import time
from itertools import cycle

from curses_tools import draw_frame, get_frame_size, read_controls
from physic import update_speed
from space_garbage import fly_garbage

ROCKET_ROWS_SPEED = 1
ROCKET_COLUMNS_SPEED = 1
STARS_COUNT_MIN = 80
STARS_COUNT_MAX = 130
STAR_SYMBOLS = '+*.:'
STARS_BORDER_OFFSET = 3
TIC_TIMEOUT = 0.1
TIC_OFFSET = (5, 25)
SPACESHIP_ANIMATION_TIC_OFFSET = 2
GARBAGE_TIC_OFFSET = (10, 20)
BORDER_OFFSET = 1

_coroutines = []


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def get_frames():
    with open('./animations/rocket_frame_1.txt') as file:
        rocket_frame_1 = file.read()

    with open('./animations/rocket_frame_2.txt') as file:
        rocket_frame_2 = file.read()

    with open('./animations/duck.txt') as file:
        duck_frame = file.read()

    with open('./animations/hubble.txt') as file:
        hubble_frame = file.read()

    with open('./animations/lamp.txt') as file:
        lamp_frame = file.read()

    with open('./animations/trash_large.txt') as file:
        trash_large = file.read()

    with open('./animations/trash_small.txt') as file:
        trash_small = file.read()

    with open('./animations/trash_xl.txt') as file:
        trash_xl = file.read()

    return {
        "rocket_frames": [rocket_frame_1, rocket_frame_2],
        "garbage_frames": [duck_frame, hubble_frame, lamp_frame, trash_large, trash_small, trash_xl],
    }


async def blink(canvas, row, column, symbol, tic_offset):
    while True:
        await sleep(tic_offset)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


def animate_stars(canvas, rows, columns, star_symbols):
    for _ in range(random.randint(STARS_COUNT_MIN, STARS_COUNT_MAX)):
        tic_offset = random.randint(*TIC_OFFSET)
        _coroutines.append(blink(
            canvas,
            row=random.randint(STARS_BORDER_OFFSET, rows - STARS_BORDER_OFFSET),
            column=random.randint(STARS_BORDER_OFFSET, columns - STARS_BORDER_OFFSET),
            symbol=random.choice(star_symbols),
            tic_offset=tic_offset,
        ))


async def animate_spaceship(canvas, start_row, start_column, rocket_frames):
    canvas_rows, canvas_columns = canvas.getmaxyx()

    rocket_row, rocket_column = start_row, start_column
    rocket_frame_rows, rocket_frame_columns = get_frame_size(rocket_frames[0])

    rows_speed = columns_speed = 0
    for rocket_frame in cycle(rocket_frames):
        for _ in range(SPACESHIP_ANIMATION_TIC_OFFSET):
            rows_direction, columns_direction, _ = read_controls(
                canvas,
                ROCKET_ROWS_SPEED,
                ROCKET_COLUMNS_SPEED,
            )
            rows_speed, columns_speed = update_speed(
                rows_speed,
                columns_speed,
                rows_direction,
                columns_direction,
            )

            rocket_row += rows_speed
            rocket_column += columns_speed

            rocket_row = max(rocket_row, BORDER_OFFSET)
            rocket_row = min(rocket_row, canvas_rows - rocket_frame_rows - BORDER_OFFSET)
            rocket_column = max(rocket_column, BORDER_OFFSET)
            rocket_column = min(rocket_column, canvas_columns - rocket_frame_columns - BORDER_OFFSET)

            draw_frame(canvas, round(rocket_row), round(rocket_column), rocket_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, round(rocket_row), round(rocket_column), rocket_frame, negative=True)


async def fill_orbit_with_garbage(canvas, columns, garbage_frames):
    while True:
        garbage_frame = random.choice(garbage_frames)
        garbage_column = random.randint(BORDER_OFFSET, columns)
        _coroutines.append(
            fly_garbage(canvas, garbage_column, garbage_frame)
        )
        tic_offset = random.randint(*GARBAGE_TIC_OFFSET)
        await sleep(tic_offset)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas_rows, canvas_columns = canvas.getmaxyx()

    frames = get_frames()
    rocket_frames = frames.get("rocket_frames")
    garbage_frames = frames.get("garbage_frames")

    animate_stars(canvas, canvas_rows, canvas_columns, STAR_SYMBOLS)
    _coroutines.extend([
        animate_spaceship(canvas, canvas_rows//2, canvas_columns//2, rocket_frames),
        fill_orbit_with_garbage(canvas, canvas_columns, garbage_frames),
    ])

    while True:
        for coroutine in _coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                _coroutines.remove(coroutine)

        canvas.refresh()
        canvas.border()
        time.sleep(TIC_TIMEOUT)
        if len(_coroutines) == 0:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
