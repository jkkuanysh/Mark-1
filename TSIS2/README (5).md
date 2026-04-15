# TSIS2 - Paint Application Extended Drawing Tools

## Files
- `paint.py` - main paint program
- `tools.py` - helper functions for toolbar, flood fill, and previews
- `assets/` - optional folder for future icons or fonts

## Features completed
- Pencil freehand tool
- Straight line tool with live preview
- Three brush sizes: 2 px, 5 px, 10 px
- Flood-fill using `get_at()` and `set_at()`
- Ctrl+S saves canvas to timestamped PNG
- Text tool:
  - click to place cursor
  - type in real time
  - Enter confirms
  - Escape cancels
- Existing shapes respect current brush size:
  - rectangle
  - circle
  - square
  - right triangle
  - equilateral triangle
  - rhombus
- Eraser included

## Run
```bash
pip install pygame
python paint.py
```

## Controls
- `P` pencil
- `L` line
- `R` rectangle
- `C` circle
- `Q` square
- `W` right triangle
- `A` equilateral triangle
- `D` rhombus
- `F` fill
- `T` text
- `E` eraser
- `1` small brush
- `2` medium brush
- `3` large brush
- `Ctrl+S` save PNG

## Notes
Saved images go into the `saved_images/` folder with a timestamp in the filename.
