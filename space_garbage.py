import asyncio

from curses_tools import draw_frame, get_frame_size


async def fly_garbage(canvas, column, garbage_frame, speed=1):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    _, frame_columns = get_frame_size(garbage_frame)

    column = max(frame_columns + 1, column)
    column = min(column, columns_number - frame_columns - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
