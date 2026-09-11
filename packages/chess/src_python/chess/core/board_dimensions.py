"""
Board geometry. Nothing anywhere else in this package writes a bare 8.

Files and ranks are numbered from one, as the schema numbers them and as they
are written: "a1" is file 1, rank 1.
"""

BOARD_SIZE = 8
FILE_COUNT = BOARD_SIZE
RANK_COUNT = BOARD_SIZE
SQUARE_COUNT = FILE_COUNT * RANK_COUNT

FIRST_FILE_NUMBER = 1
LAST_FILE_NUMBER = FIRST_FILE_NUMBER + FILE_COUNT - 1
FIRST_RANK_NUMBER = 1
LAST_RANK_NUMBER = FIRST_RANK_NUMBER + RANK_COUNT - 1
