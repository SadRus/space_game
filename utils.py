import asyncio
import curses

from game_scenario import PHRASES


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
        'rocket_frames': [
            rocket_frame_1,
            rocket_frame_2,
        ],
        'garbage_frames': [
            duck_frame,
            hubble_frame,
            lamp_frame,
            trash_large,
            trash_small,
            trash_xl,
        ],
    }


async def sleep(tics=1):
    if not tics:
        await asyncio.sleep(0)
    for _ in range(tics):
        await asyncio.sleep(0)


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


async def display_statistics(canvas, ctx_year):
    canvas_rows, canvas_columns = canvas.getmaxyx()
    subwindow = canvas.derwin(3, canvas_columns, canvas_rows - 3, 0)

    while True:
        current_year = ctx_year.get()
        subwindow.addstr(1, 1, f'Year: {str(current_year)}', curses.A_BOLD)
        year_achievement_phrase = PHRASES.get(current_year, "")
        if year_achievement_phrase:
            subwindow.addstr(1, 15, year_achievement_phrase, curses.A_BOLD)
        subwindow.refresh()
        await sleep(15)
        subwindow.addstr(1, 15, " " * len(year_achievement_phrase), curses.A_BOLD)


async def uplevel_hard(ctx_year):
    while True:
        await sleep(15)
        current_year = ctx_year.get()
        next_year = current_year + 1
        ctx_year.set(next_year)
