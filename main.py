import asyncio
import curses
import random
import time

TIC_TIMEOUT = 0.1


async def blink(canvas: curses.window, row: int, column: int, symbol='*'):
    for _ in range(random.randint(10, 20)):
        await asyncio.sleep(0)
    while True:
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


def draw(canvas: curses.window) -> None:
    curses.curs_set(False)
    canvas.border()
    star_symbols = "+*.:"
    window_height, window_width = canvas.getmaxyx()

    coroutines = []
    for _ in range(random.randint(70, 130)):
        coroutines.append(blink(
            canvas,
            row=random.randint(5, window_height - 5),
            column=random.randint(5, window_width - 5),
            symbol=random.choice(star_symbols),
        ))
    while True:
        for coroutine in coroutines:
            coroutine.send(None)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)

    # canvas.addstr(row, column, "*", curses.A_DIM)
    # time.sleep(1)
    # canvas.refresh()
    # canvas.addstr(row, column, "*")
    # time.sleep(0.3)
    # canvas.refresh()
    # canvas.addstr(row, column, "*", curses.A_BOLD)
    # time.sleep(0.5)
    # canvas.refresh()
    # canvas.addstr(row, column, "*")
    # time.sleep(0.3)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.wrapper(draw)
