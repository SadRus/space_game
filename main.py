import time
import curses


def draw(canvas: curses.window) -> None:
    curses.curs_set(False)
    canvas.border()
    row, column = (5, 20)

    canvas.addstr(row, column, "*", curses.A_DIM)
    time.sleep(1)
    canvas.refresh()
    canvas.addstr(row, column, "*")
    time.sleep(0.3)
    canvas.refresh()
    canvas.addstr(row, column, "*", curses.A_BOLD)
    time.sleep(0.5)
    canvas.refresh()
    canvas.addstr(row, column, "*")
    time.sleep(0.3)
    canvas.refresh()


if __name__ == "__main__":
    curses.update_lines_cols()
    while True:
        curses.wrapper(draw)
