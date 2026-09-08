"""
Board geometry. Nothing anywhere else in this package writes a bare 8.
"""

BOARD_SIZE = 8
FILE_COUNT = BOARD_SIZE
RANK_COUNT = BOARD_SIZE
SQUARE_COUNT = FILE_COUNT * RANK_COUNT

# Files and ranks are indexed from zero so they can address a grid, but they are
# written "a1" through "h8". These name the gap between the two.
FIRST_FILE_INDEX = 0
FIRST_RANK_INDEX = 0
RANK_LABEL_OFFSET = 1
