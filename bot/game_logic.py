import random
import copy

SIZE = 4

def new_grid():
    return [[0 for _ in range(SIZE)] for _ in range(SIZE)]

def add_random_tile(grid):
    empty = [(i, j) for i in range(SIZE) for j in range(SIZE) if grid[i][j] == 0]
    if not empty:
        return grid
    i, j = random.choice(empty)
    grid[i][j] = random.choices([2, 4], [0.9, 0.1])[0]
    return grid

def compress(row):
    new_row = [i for i in row if i != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row

def merge(row):
    for i in range(SIZE - 1):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
    return row

def move_left(grid):
    score = 0
    new_grid = []
    for row in grid:
        compressed = compress(row)
        merged = merge(compressed)
        compressed = compress(merged)
        score += sum([merged[i] for i in range(SIZE) if merged[i] != row[i]])
        new_grid.append(compressed)
    return new_grid, score

def rotate(grid):
    return [list(row) for row in zip(*grid[::-1])]

def move(grid, direction):
    temp_grid = copy.deepcopy(grid)
    score = 0
    if direction == 'left':
        temp_grid, score = move_left(temp_grid)
    elif direction == 'right':
        temp_grid = [row[::-1] for row in temp_grid]
        temp_grid, score = move_left(temp_grid)
        temp_grid = [row[::-1] for row in temp_grid]
    elif direction == 'up':
        temp_grid = rotate(temp_grid)
        temp_grid, score = move_left(temp_grid)
        temp_grid = rotate(rotate(rotate(temp_grid)))
    elif direction == 'down':
        temp_grid = rotate(temp_grid)
        temp_grid = [row[::-1] for row in temp_grid]
        temp_grid, score = move_left(temp_grid)
        temp_grid = [row[::-1] for row in temp_grid]
        temp_grid = rotate(rotate(rotate(temp_grid)))
    return temp_grid, score

def can_move(grid):
    for i in range(SIZE):
        for j in range(SIZE):
            if grid[i][j] == 0:
                return True
            if i < SIZE-1 and grid[i][j] == grid[i+1][j]:
                return True
            if j < SIZE-1 and grid[i][j] == grid[i][j+1]:
                return True
    return False

def is_win(grid):
    return any(2048 in row for row in grid)