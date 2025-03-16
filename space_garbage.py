import asyncio

from curses_tools import draw_frame, get_frame_size
from obstacles import Obstacle

obstacles = []


async def fly_garbage(canvas, column, garbage_frame, speed=1):
    """
    Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start.
    """
    rows_number, columns_number = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(garbage_frame)

    column = max(frame_columns + 1, column)
    column = min(column, columns_number - frame_columns - 1)

    row = 0

    obstacle = Obstacle(
        row=row,
        column=column,
        rows_size=frame_rows,
        columns_size=frame_columns,
    )
    obstacles.append(obstacle)

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)

        row += speed
        obstacle.row += speed
