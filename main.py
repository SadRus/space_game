import asyncio
import curses
import time

TIC_TIMEOUT = 0.1


async def blink(canvas: curses.window, row, column, symbol='*'):
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
    coroutines = [
        blink(canvas, row=5, column=5),
        blink(canvas, row=5, column=10),
        blink(canvas, row=5, column=15),
        blink(canvas, row=5, column=20),
        blink(canvas, row=5, column=25),
    ]
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
