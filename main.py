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


def draw(canvas: curses.window) -> None:
    curses.curs_set(False)
    canvas.border()
    star_symbols = "+*.:"
    rows, columns = canvas.getmaxyx()

    coroutines = [
        fire(canvas, rows/2, columns/2),
    ]
    for _ in range(random.randint(70, 130)):
        coroutines.append(blink(
            canvas,
            row=random.randint(5, rows - 5),
            column=random.randint(5, columns - 5),
            symbol=random.choice(star_symbols),
        ))
    while True:
        try:
            for coroutine in coroutines:
                coroutine.send(None)
            canvas.refresh()
            time.sleep(TIC_TIMEOUT)
        except StopIteration:
            coroutines.remove(coroutine)

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
