import asyncio
import curses
import random
import time

from itertools import cycle

from contextvars import ContextVar
from curses_tools import (
    draw_frame,
    get_frame_size,
    read_controls,
    show_gameover,
)
from fire_animation import fire
from game_scenario import get_garbage_delay_tics
from obstacles import obstacles
from physic import update_speed
from space_garbage import fly_garbage
from utils import (
    blink,
    display_statistics,
    get_frames,
    sleep,
    uplevel_hard,
)

ROCKET_ROWS_SPEED = 1
ROCKET_COLUMNS_SPEED = 1
STARS_COUNT_MIN = 80
STARS_COUNT_MAX = 130
STAR_SYMBOLS = '+*.:'
STARS_BORDER_OFFSET = 3
TIC_TIMEOUT = 0.1
TIC_OFFSET = (5, 25)
SPACESHIP_ANIMATION_TIC_OFFSET = 2
YEAR = ContextVar('YEAR', default=1957)

BORDER_OFFSET = 1

_coroutines = []


async def animate_stars(canvas, rows, columns, star_symbols):
    for _ in range(random.randint(STARS_COUNT_MIN, STARS_COUNT_MAX)):
        tic_offset = random.randint(*TIC_OFFSET)
        _coroutines.append(blink(
            canvas,
            row=random.randint(STARS_BORDER_OFFSET, rows - STARS_BORDER_OFFSET),
            column=random.randint(STARS_BORDER_OFFSET, columns - STARS_BORDER_OFFSET),
            symbol=random.choice(star_symbols),
            tic_offset=tic_offset,
        ))


async def animate_spaceship(canvas, start_row, rocket_start_column, rocket_frames):
    canvas_rows, canvas_columns = canvas.getmaxyx()

    rocket_row, rocket_column = start_row, rocket_start_column
    rocket_frame_rows, rocket_frame_columns = get_frame_size(rocket_frames[0])
    rows_speed = columns_speed = 0

    for rocket_frame in cycle(rocket_frames):
        for _ in range(SPACESHIP_ANIMATION_TIC_OFFSET):
            rows_direction, columns_direction, space_pressed = read_controls(
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

            if space_pressed:
                rocket_start_column = rocket_column + rocket_frame_columns // 2
                _coroutines.append(
                    fire(canvas, start_row=rocket_row, start_column=rocket_start_column),
                )

            rocket_row = max(rocket_row, BORDER_OFFSET)
            rocket_row = min(rocket_row, canvas_rows - rocket_frame_rows - BORDER_OFFSET)
            rocket_column = max(rocket_column, BORDER_OFFSET)
            rocket_column = min(rocket_column, canvas_columns - rocket_frame_columns - BORDER_OFFSET)

            draw_frame(canvas, round(rocket_row), round(rocket_column), rocket_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, round(rocket_row), round(rocket_column), rocket_frame, negative=True)

            for obstacle in obstacles:
                if obstacle.has_collision(rocket_row, rocket_column):
                    with open('./animations/game_over.txt') as file:
                        text_frame = file.read()
                    await show_gameover(canvas, text_frame)


async def fill_orbit_with_garbage(canvas, columns, garbage_frames):
    while True:
        current_year = YEAR.get()
        tic_offset = get_garbage_delay_tics(current_year)

        if tic_offset is None:
            await sleep(0)
        else:
            garbage_frame = random.choice(garbage_frames)
            garbage_column = random.randint(BORDER_OFFSET, columns)
            _coroutines.extend([
                fly_garbage(canvas, garbage_column, garbage_frame),
            ])
            await sleep(tic_offset)


def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas_rows, canvas_columns = canvas.getmaxyx()

    frames = get_frames()
    rocket_frames = frames.get('rocket_frames')
    garbage_frames = frames.get('garbage_frames')
    _coroutines.extend([
        uplevel_hard(YEAR),
        display_statistics(canvas, YEAR),
        animate_stars(canvas, canvas_rows, canvas_columns, STAR_SYMBOLS),
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
        if not _coroutines:
            break


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
