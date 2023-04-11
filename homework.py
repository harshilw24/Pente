import copy
import math
import os.path
import random
import time

input_list = list()

with open('input.txt', 'rt') as input_file:
    for line in input_file.readlines():
        input_list.append(line.strip())

if input_list[0] == 'WHITE':
    player = 'w'
    opponent = 'b'
else:
    player = 'b'
    opponent = 'w'
playtime = float(input_list[1])
captures = [int(x) for x in input_list[2].split(',')]  # captures of [0] is for white and [1] is for black
board = []
max_depth = 1

#  parsing the playing playing_board
for i in range(19):
    board_line = [str(x) for x in input_list[i + 3].split()]
    board.append(board_line)

#  calculating capture score
if player == 'w':
    capture_difference = captures[0] - captures[1]
else:
    capture_difference = captures[1] - captures[0]


#  generating the output file
def write_output(incoming):
    output_file = open('output.txt', 'w')
    playdata = open('playdata.txt', 'a')
    playdata.write("{}\n".format(str(incoming[0]) + ' ' + str(incoming[1])))
    st = 'ABCDEFGHJKLMNOPQRST'
    incoming[0] = str(19 - incoming[0])
    incoming[1] = str(st[incoming[1]])
    output_file.write(incoming[0] + incoming[1])
    output_file.close()
    playdata.close()


def remove_captures(playing_board, p):
    o = 'b' if p == 'w' else 'w'
    for x in range(19):
        for y in range(19):
            if playing_board[x][y] == p:
                # Check horizontally
                if y < 16 and playing_board[x][y + 1] == o and playing_board[x][y + 2] == o \
                        and playing_board[x][y + 3] == p:
                    playing_board[x][y + 1] = '.'
                    playing_board[x][y + 2] = '.'

                # Check vertically
                if x < 16 and playing_board[x + 1][y] == o and playing_board[x + 2][y] == o \
                        and playing_board[x + 3][y] == p:
                    playing_board[x + 1][y] = '.'
                    playing_board[x + 2][y] = '.'

                # Check diagonally (positive slope)
                if x < 16 and y < 16 and playing_board[x + 1][y + 1] == o and playing_board[x + 2][y + 2] == o \
                        and playing_board[x + 3][y + 3] == p:
                    playing_board[x + 1][y + 1] = '.'
                    playing_board[x + 2][y + 2] = '.'

                # Check diagonally (negative slope)
                if x < 16 and y > 2 and playing_board[x + 1][y - 1] == o and playing_board[x + 2][y - 2] == o \
                        and playing_board[x + 3][y - 3] == p:
                    playing_board[x + 1][y - 1] = '.'
                    playing_board[x + 2][y - 2] = '.'
    return playing_board


def make_move(b, p, move):
    row, col = move
    b[row][col] = p
    if get_num_captures(b, p, None) > 0:
        remove_captures(b, p)
    return b


def is_alone(pb, row, col):
    if pb[row][col + 1] == '.' and pb[row][col - 1] == '.' and pb[row + 1][col] == '.' and pb[row - 1][col] == '.' and \
            pb[row + 1][col + 1] == '.' and pb[row - 1][col - 1] == '.' and pb[row + 1][col - 1] == '.' and \
            pb[row - 1][col] == '.' and pb[row - 1][col + 1] == '.':
        return True
    else:
        return False


def get_moves(pb, ranges=None):
    if max_depth == 1:
        ranges = None
    if ranges is None:
        possible_moves = []
        for x in range(19):
            for y in range(19):
                if pb[x][y] == '.':
                    possible_moves.append([x, y])
        return possible_moves
    else:
        possible_moves = []
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for y in range(ranges["y1"], ranges["y2"] + 1):
                if pb[x][y] == '.' and not is_alone(pb, x, y):
                    possible_moves.append([x, y])

        return possible_moves


def count_pieces(playing_board, p, ranges):
    count = 0
    if ranges is None:
        for row in playing_board:
            for cell in row:
                if cell == p:
                    count += 1
        return count
    else:
        for row in range(ranges["x1"], ranges["x2"] + 1):
            for cell in range(ranges["y1"], ranges["y2"] + 1):
                if playing_board[row][cell] == p:
                    count += 1
        return count


def count_pieces_all(pb, ranges):
    count = 0
    for row in range(ranges["x1"], ranges["x2"] + 1):
        for cell in range(ranges["y1"], ranges["y2"] + 1):
            if pb[row][cell] != '.':
                count += 1
    return count


def density_centre(pb):
    m = 0
    best = None
    for x in range(len(pb)):
        for y in range(len(pb[0])):
            x1v = max(x - 4, 0)
            x2v = min(x + 4, 18)
            y1v = max(y - 4, 0)
            y2v = min(y + 4, 18)
            count = count_pieces_all(pb, dict(x1=x1v, x2=x2v, y1=y1v, y2=y2v))
            if count > m:
                m = count
                best = [x, y]
    return best


def get_colour(playing_board, row, col):
    return playing_board[row][col]


def get_num_captures(playing_board, p, ranges):
    o = 'b' if p == 'w' else 'w'  # opponent's color
    capture_count = 0
    if ranges is None:
        for x in range(19):
            for y in range(19):
                if playing_board[x][y] == p:
                    # Check horizontally
                    if y < 16 and playing_board[x][y + 1] == o and playing_board[x][y + 2] == o \
                            and playing_board[x][y + 3] == p:
                        capture_count += 1

                    # Check vertically
                    if x < 16 and playing_board[x + 1][y] == o and playing_board[x + 2][y] == o \
                            and playing_board[x + 3][y] == p:
                        capture_count += 1

                    # Check diagonally (positive slope)
                    if x < 16 and y < 16 and playing_board[x + 1][y + 1] == o and playing_board[x + 2][y + 2] == o \
                            and playing_board[x + 3][y + 3] == p:
                        capture_count += 1

                    # Check diagonally (negative slope)
                    if x < 16 and y > 2 and playing_board[x + 1][y - 1] == o and playing_board[x + 2][y - 2] == o \
                            and playing_board[x + 3][y - 3] == p:
                        capture_count += 1

        return capture_count

    else:
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for y in range(ranges["y1"], ranges["y2"] + 1):
                if playing_board[x][y] == p:
                    # Check horizontally
                    if y < 16 and playing_board[x][y + 1] == o and playing_board[x][y + 2] == o \
                            and playing_board[x][y + 3] == p:
                        capture_count += 1

                    # Check vertically
                    if x < 16 and playing_board[x + 1][y] == o and playing_board[x + 2][y] == o \
                            and playing_board[x + 3][y] == p:
                        capture_count += 1

                    # Check diagonally (positive slope)
                    if x < 16 and y < 16 and playing_board[x + 1][y + 1] == o and playing_board[x + 2][y + 2] == o \
                            and playing_board[x + 3][y + 3] == p:
                        capture_count += 1

                    # Check diagonally (negative slope)
                    if x < 16 and y > 2 and playing_board[x + 1][y - 1] == o and playing_board[x + 2][y - 2] == o \
                            and playing_board[x + 3][y - 3] == p:
                        capture_count += 1

            return capture_count


def get_num_potential_captures(playing_board, p, ranges):
    count = 0
    if p == 'w':
        o = 'b'
    else:
        o = 'w'

    if ranges is None:
        # Check for captures horizontally
        for x in range(19):
            for j in range(16):
                if playing_board[x][j] == "." and playing_board[x][j + 1] == o and playing_board[x][j + 2] == o and \
                        playing_board[x][j + 3] == p:
                    count += 1
                if playing_board[x][j] == p and playing_board[x][j + 1] == o and playing_board[x][j + 2] == o and \
                        playing_board[x][j + 3] == ".":
                    count += 1
        # Check for captures vertically
        for x in range(16):
            for j in range(19):
                if playing_board[x][j] == "." and playing_board[x + 1][j] == o and playing_board[x + 2][j] == o and \
                        playing_board[x + 3][j] == p:
                    count += 1
                if playing_board[x][j] == p and playing_board[x + 1][j] == o and playing_board[x + 2][j] == o and \
                        playing_board[x + 3][j] == '.':
                    count += 1
        # Check for captures diagonally (top-left to bottom-right)
        for x in range(16):
            for j in range(16):
                if playing_board[x][j] == "." and playing_board[x + 1][j + 1] == o and playing_board[x + 2][j + 2] == o\
                        and playing_board[x + 3][j + 3] == p:
                    count += 1
                if playing_board[x][j] == p and playing_board[x + 1][j + 1] == o and playing_board[x + 2][j + 2] == o \
                        and playing_board[x + 3][j + 3] == '.':
                    count += 1
        # Check for captures diagonally (top-right to bottom-left)
        for x in range(16):
            for j in range(3, 19):
                if playing_board[x][j] == p and playing_board[x + 1][j - 1] == o and playing_board[x + 2][j - 2] == o \
                        and playing_board[x + 3][j - 3] == ".":
                    count += 1
                if playing_board[x][j] == '.' and playing_board[x + 1][j - 1] == o and playing_board[x + 2][j - 2] == o\
                        and playing_board[x + 3][j - 3] == p:
                    count += 1
        return count
    else:
        # Check for captures horizontally
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for j in range(ranges["y1"], min(16, ranges["y2"] + 1)):
                if playing_board[x][j] == "." and playing_board[x][j + 1] == o and playing_board[x][j + 2] == o and \
                        playing_board[x][j + 3] == p:
                    count += 1
                if playing_board[x][j] == p and playing_board[x][j + 1] == o and playing_board[x][j + 2] == o and \
                        playing_board[x][j + 3] == ".":
                    count += 1
        # Check for captures vertically
        for x in range(ranges["x1"], min(16, ranges["x2"] + 1)):
            for j in range(ranges["y1"], ranges["y2"] + 1):
                if playing_board[x][j] == "." and playing_board[x + 1][j] == o and playing_board[x + 2][j] == o and \
                        playing_board[x + 3][j] == p:
                    count += 1
                if playing_board[x][j] == p and playing_board[x + 1][j] == o and playing_board[x + 2][j] == o and \
                        playing_board[x + 3][j] == '.':
                    count += 1
        # Check for captures diagonally (top-left to bottom-right)
        for x in range(ranges["x1"], min(16, ranges["x2"] + 1)):
            for j in range(ranges["y1"], min(16, ranges["y2"] + 1)):
                if playing_board[x][j] == "." and playing_board[x + 1][j + 1] == o and playing_board[x + 2][j + 2] == o\
                        and playing_board[x + 3][j + 3] == p:
                    count += 1
                if playing_board[x][j] == p and playing_board[x + 1][j + 1] == o and playing_board[x + 2][j + 2] == o \
                        and playing_board[x + 3][j + 3] == '.':
                    count += 1
        # Check for captures diagonally (top-right to bottom-left)
        for x in range(ranges["x1"], min(16, ranges["x2"] + 1)):
            for j in range(max(3, ranges["y1"]), ranges["y2"] + 1):
                if playing_board[x][j] == p and playing_board[x + 1][j - 1] == o and playing_board[x + 2][j - 2] == o \
                        and playing_board[x + 3][j - 3] == ".":
                    count += 1
                if playing_board[x][j] == '.' and playing_board[x + 1][j - 1] == o and playing_board[x + 2][j - 2] == o\
                        and playing_board[x + 3][j - 3] == p:
                    count += 1
        return count


def count_open_fours(playing_board, color, ranges):
    count = 0
    if ranges is None:
        for x in range(len(playing_board)):
            for j in range(len(playing_board[0])):
                # Check for sequence in horizontal direction
                if j < 15 and playing_board[x][j] == '.' and playing_board[x][j + 1] == color and \
                        playing_board[x][j + 2] == color and playing_board[x][j + 3] == color and \
                        playing_board[x][j + 4] == color and playing_board[x][j + 5] == '.':
                    count += 1
                # Check for sequence in vertical direction
                if x < 15 and playing_board[x][j] == '.' and playing_board[x + 1][j] == color \
                        and playing_board[x + 2][j] == color and playing_board[x + 3][j] == color \
                        and playing_board[x + 4][j] == color and playing_board[x + 5][j] == '.':
                    count += 1
                # Check for sequence in diagonal direction (top-left to bottom-right)
                if x < 15 and j < 15 and playing_board[x][j] == '.' and playing_board[x + 1][j + 1] == color and \
                        playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color and \
                        playing_board[x + 4][j + 4] == color and playing_board[x + 5][j + 5] == '.':
                    count += 1
                # Check for sequence in diagonal direction (bottom-left to top-right)
                if x > 3 and j < 15 and playing_board[x][j] == '.' and playing_board[x - 1][j + 1] == color and \
                        playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color and \
                        playing_board[x - 4][j + 4] == color and playing_board[x - 5][j + 5] == '.':
                    count += 1
        return count
    else:
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for j in range(ranges["y1"], ranges["y2"] + 1):
                # Check for sequence in horizontal direction
                if j < 15 and playing_board[x][j] == '.' and playing_board[x][j + 1] == color and \
                        playing_board[x][j + 2] == color and playing_board[x][j + 3] == color and \
                        playing_board[x][j + 4] == color and playing_board[x][j + 5] == '.':
                    count += 1
                # Check for sequence in vertical direction
                if x < 15 and playing_board[x][j] == '.' and playing_board[x + 1][j] == color and \
                        playing_board[x + 2][j] == color and playing_board[x + 3][j] == color and \
                        playing_board[x + 4][j] == color and playing_board[x + 5][j] == '.':
                    count += 1
                # Check for sequence in diagonal direction (top-left to bottom-right)
                if x < 15 and j < 15 and playing_board[x][j] == '.' and playing_board[x + 1][j + 1] == color and \
                        playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color and \
                        playing_board[x + 4][j + 4] == color and playing_board[x + 5][j + 5] == '.':
                    count += 1
                # Check for sequence in diagonal direction (bottom-left to top-right)
                if x > 3 and j < 15 and playing_board[x][j] == '.' and playing_board[x - 1][j + 1] == color and \
                        playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color and \
                        playing_board[x - 4][j + 4] == color and playing_board[x - 5][j + 5] == '.':
                    count += 1
        return count


def count_closed_fours(playing_board, color, ranges):
    count = 0
    anti = 'b' if color == 'w' else 'w'

    if ranges is None:
        for x in range(len(playing_board)):
            for j in range(len(playing_board[0])):
                # Check horizontal
                if j <= 14 and playing_board[x][j] == color and playing_board[x][j + 1] == color \
                        and playing_board[x][j + 2] == color and playing_board[x][j + 3] == color \
                        and (j == 0 or playing_board[x][j - 1] == anti) and playing_board[x][j + 4] == '.':
                    count += 1
                if j <= 14 and playing_board[x][j] == color and playing_board[x][j + 1] == color \
                        and playing_board[x][j + 2] == color and playing_board[x][j + 3] == color \
                        and (j == 0 or playing_board[x][j - 1] == '.') and playing_board[x][j + 4] == anti:
                    count += 1
                # Check vertical
                if x <= 14 and playing_board[x][j] == color and playing_board[x + 1][j] == color \
                        and playing_board[x + 2][j] == color and playing_board[x + 3][j] == color \
                        and (x == 0 or playing_board[x - 1][j] == anti) and playing_board[x + 4][j] == '.':
                    count += 1
                if x <= 14 and playing_board[x][j] == color and playing_board[x + 1][j] == color \
                        and playing_board[x + 2][j] == color and playing_board[x + 3][j] == color \
                        and (x == 0 or playing_board[x - 1][j] == '.') and playing_board[x + 4][j] == anti:
                    count += 1
                # Check diagonal (top-left to bottom-right)
                if x <= 14 and j <= 14 and playing_board[x][j] == color and playing_board[x + 1][j + 1] == color \
                        and playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color \
                        and ((x == 0 or j == 0) or playing_board[x - 1][j - 1] == anti) and \
                        (x == 14 or j == 14 or playing_board[x + 4][j + 4] == '.'):
                    count += 1
                if x <= 14 and j <= 14 and playing_board[x][j] == color and playing_board[x + 1][j + 1] == color \
                        and playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color \
                        and ((x == 0 or j == 0) or playing_board[x - 1][j - 1] == '.') and \
                        (x == 14 or j == 14 or playing_board[x + 4][j + 4] == anti):
                    count += 1
                # Check diagonal (bottom-left to top-right)
                if x >= 4 and j <= 14 and playing_board[x][j] == color and playing_board[x - 1][j + 1] == color \
                        and playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color \
                        and ((x == 18 or j == 0) or playing_board[x + 1][j - 1] == '.') and \
                        (x == 4 or j == 14 or playing_board[x - 4][j + 4] == anti):
                    count += 1
                if x >= 4 and j <= 14 and playing_board[x][j] == color and playing_board[x - 1][j + 1] == color \
                        and playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color \
                        and ((x == 18 or j == 0) or playing_board[x + 1][j - 1] == anti) and \
                        (x == 4 or j == 14 or playing_board[x - 4][j + 4] == '.'):
                    count += 1
        return count
    else:
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for j in range(ranges["y1"], ranges["y2"] + 1):
                # Check horizontal
                if j <= 14 and playing_board[x][j] == color and playing_board[x][j + 1] == color \
                        and playing_board[x][j + 2] == color and playing_board[x][j + 3] == color \
                        and (j == 0 or playing_board[x][j - 1] == anti) and playing_board[x][j + 4] == '.':
                    count += 1
                if j <= 14 and playing_board[x][j] == color and playing_board[x][j + 1] == color \
                        and playing_board[x][j + 2] == color and playing_board[x][j + 3] == color \
                        and (j == 0 or playing_board[x][j - 1] == '.') and playing_board[x][j + 4] == anti:
                    count += 1
                # Check vertical
                if x <= 14 and playing_board[x][j] == color and playing_board[x + 1][j] == color \
                        and playing_board[x + 2][j] == color and playing_board[x + 3][j] == color \
                        and (x == 0 or playing_board[x - 1][j] == anti) and playing_board[x + 4][j] == '.':
                    count += 1
                if x <= 14 and playing_board[x][j] == color and playing_board[x + 1][j] == color \
                        and playing_board[x + 2][j] == color and playing_board[x + 3][j] == color \
                        and (x == 0 or playing_board[x - 1][j] == '.') and playing_board[x + 4][j] == anti:
                    count += 1
                # Check diagonal (top-left to bottom-right)
                if x <= 14 and j <= 14 and playing_board[x][j] == color and playing_board[x + 1][j + 1] == color \
                        and playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color \
                        and ((x == 0 or j == 0) or playing_board[x - 1][j - 1] == anti) and \
                        (x == 14 or j == 14 or playing_board[x + 4][j + 4] == '.'):
                    count += 1
                if x <= 14 and j <= 14 and playing_board[x][j] == color and playing_board[x + 1][j + 1] == color \
                        and playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color \
                        and ((x == 0 or j == 0) or playing_board[x - 1][j - 1] == '.') and \
                        (x == 14 or j == 14 or playing_board[x + 4][j + 4] == anti):
                    count += 1
                # Check diagonal (bottom-left to top-right)
                if x >= 4 and j <= 14 and playing_board[x][j] == color and playing_board[x - 1][j + 1] == color \
                        and playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color \
                        and ((x == 18 or j == 0) or playing_board[x + 1][j - 1] == '.') and \
                        (x == 4 or j == 14 or playing_board[x - 4][j + 4] == anti):
                    count += 1
                if x >= 4 and j <= 14 and playing_board[x][j] == color and playing_board[x - 1][j + 1] == color \
                        and playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color \
                        and ((x == 18 or j == 0) or playing_board[x + 1][j - 1] == anti) and \
                        (x == 4 or j == 14 or playing_board[x - 4][j + 4] == '.'):
                    count += 1
        return count


def count_two_connect(playing_board, p, ranges):
    # Define the o's color
    o = 'b' if p == 'w' else 'w'

    # Initialize the count of two-connects
    two_connect_count = 0

    if ranges is None:
        # Check each position on the playing_board
        for x in range(19):
            for j in range(19):
                # Check horizontally to the right
                if j <= 14:
                    if playing_board[x][j] == p and playing_board[x][j + 1:j + 5].count(o) == 0 and \
                            playing_board[x][j + 1:j + 5].count(p) >= 1:
                        two_connect_count += 1
                # Check vertically downwards
                if x <= 14:
                    if playing_board[x][j] == p and [playing_board[k][j] for k in range(x + 1, x + 5)].count(o) == 0 \
                            and [playing_board[k][j] for k in range(x + 1, x + 5)].count(p) >= 1:
                        two_connect_count += 1
                # Check diagonally downwards to the right
                if x <= 14 and j <= 14:
                    if playing_board[x][j] == p and [playing_board[x + k][j + k] for k in range(1, 5)].count(o) == 0 \
                            and [playing_board[x + k][j + k] for k in range(1, 5)].count(p) >= 1:
                        two_connect_count += 1
                # Check diagonally upwards to the right
                if x >= 4 and j <= 14:
                    if playing_board[x][j] == p and [playing_board[x - k][j + k] for k in range(1, 5)].count(o) == 0 \
                            and [playing_board[x - k][j + k] for k in range(1, 5)].count(p) >= 1:
                        two_connect_count += 1

        return two_connect_count

    else:
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for j in range(ranges["y1"], ranges["y2"] + 1):
                # Check horizontally to the right
                if j <= 14:
                    if playing_board[x][j] == p and playing_board[x][j + 1:j + 5].count(o) == 0 and \
                            playing_board[x][j + 1:j + 5].count(p) >= 1:
                        two_connect_count += 1
                # Check vertically downwards
                if x <= 14:
                    if playing_board[x][j] == p and [playing_board[k][j] for k in range(x + 1, x + 5)].count(o) == 0 \
                            and [playing_board[k][j] for k in range(x + 1, x + 5)].count(p) >= 1:
                        two_connect_count += 1
                # Check diagonally downwards to the right
                if x <= 14 and j <= 14:
                    if playing_board[x][j] == p and [playing_board[x + k][j + k] for k in range(1, 5)].count(o) == 0 \
                            and [playing_board[x + k][j + k] for k in range(1, 5)].count(p) >= 1:
                        two_connect_count += 1
                # Check diagonally upwards to the right
                if x >= 4 and j <= 14:
                    if playing_board[x][j] == p and [playing_board[x - k][j + k] for k in range(1, 5)].count(o) == 0 \
                            and [playing_board[x - k][j + k] for k in range(1, 5)].count(p) >= 1:
                        two_connect_count += 1

        return two_connect_count


def count_closed_threes(playing_board, color, ranges):
    count = 0
    anti = 'b' if color == 'w' else 'w'
    rows = len(playing_board)
    cols = len(playing_board[0])

    if ranges is None:
        for x in range(rows):
            for j in range(cols):
                if j <= cols - 4 and playing_board[x][j] == color and playing_board[x][j + 1] == color and \
                        playing_board[x][j + 2] == color:
                    if (j == 0 or playing_board[x][j - 1] == anti) and playing_board[x][j + 3] == '.':
                        count += 1
                    elif (j == cols - 4 or playing_board[x][j + 3] == anti) and playing_board[x][j - 1] == '.':
                        count += 1

                if x <= rows - 4 and playing_board[x][j] == color and playing_board[x + 1][j] == color and \
                        playing_board[x + 2][j] == color:
                    if (x == 0 or playing_board[x - 1][j] == anti) and playing_board[x + 3][j] == '.':
                        count += 1
                    elif (x == rows - 4 or playing_board[x + 3][j] == anti) and playing_board[x - 1][j] == '.':
                        count += 1

                if x <= rows - 4 and j <= cols - 4 and playing_board[x][j] == color and \
                        playing_board[x + 1][j + 1] == color and playing_board[x + 2][j + 2] == color:
                    if (x == 0 or j == 0 or playing_board[x - 1][j - 1] == anti) and playing_board[x + 3][j + 3] == '.':
                        count += 1
                    elif (x == rows - 4 or j == cols - 4 or playing_board[x + 3][j + 3] == anti) and \
                            playing_board[x - 1][j - 1] == '.':
                        count += 1

                if x >= 3 and j <= cols - 4 and playing_board[x][j] == color and playing_board[x - 1][j + 1] == color \
                        and playing_board[x - 2][j + 2] == color:
                    if (x == rows - 1 or j == 0 or playing_board[x + 1][j - 1] == anti) and \
                            playing_board[x - 3][j + 3] == '.':
                        count += 1
                    elif (x == 2 or j == cols - 4 or playing_board[x - 3][j + 3] == anti) and \
                            playing_board[x + 1][j - 1] == '.':
                        count += 1

        return count
    else:
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for j in range(ranges["y1"], ranges["y2"] + 1):
                if j <= cols - 4 and playing_board[x][j] == color and playing_board[x][j + 1] == color and \
                        playing_board[x][j + 2] == color:
                    if (j == 0 or playing_board[x][j - 1] == anti) and playing_board[x][j + 3] == '.':
                        count += 1
                    elif (j == cols - 4 or playing_board[x][j + 3] == anti) and playing_board[x][j - 1] == '.':
                        count += 1

                if x <= rows - 4 and playing_board[x][j] == color and playing_board[x + 1][j] == color and \
                        playing_board[x + 2][j] == color:
                    if (x == 0 or playing_board[x - 1][j] == anti) and playing_board[x + 3][j] == '.':
                        count += 1
                    elif (x == rows - 4 or playing_board[x + 3][j] == anti) and playing_board[x - 1][j] == '.':
                        count += 1

                if x <= rows - 4 and j <= cols - 4 and playing_board[x][j] == color and \
                        playing_board[x + 1][j + 1] == color and playing_board[x + 2][j + 2] == color:
                    if (x == 0 or j == 0 or playing_board[x - 1][j - 1] == anti) and playing_board[x + 3][j + 3] == '.':
                        count += 1
                    elif (x == rows - 4 or j == cols - 4 or playing_board[x + 3][j + 3] == anti) and \
                            playing_board[x - 1][j - 1] == '.':
                        count += 1

                if x >= 3 and j <= cols - 4 and playing_board[x][j] == color and playing_board[x - 1][
                    j + 1] == color and \
                        playing_board[x - 2][j + 2] == color:
                    if (x == rows - 1 or j == 0 or playing_board[x + 1][j - 1] == anti) and \
                            playing_board[x - 3][j + 3] == '.':
                        count += 1
                    elif (x == 2 or j == cols - 4 or playing_board[x - 3][j + 3] == anti) and \
                            playing_board[x + 1][j - 1] == '.':
                        count += 1

        return count


def check_five_in_a_row(playing_board, color, ranges):
    if ranges is None:
        for x in range(len(playing_board)):
            for j in range(len(playing_board[0])):
                if x <= 14 and playing_board[x][j] == color and playing_board[x + 1][j] == color and \
                        playing_board[x + 2][j] == color and playing_board[x + 3][j] == color and \
                        playing_board[x + 4][j] == color:
                    return 1  # Found 5 in a row vertically
                elif j <= 14 and playing_board[x][j] == color and playing_board[x][j + 1] == color and \
                        playing_board[x][j + 2] == color and playing_board[x][j + 3] == color and \
                        playing_board[x][j + 4] == color:
                    return 1  # Found 5 in a row horizontally
                elif x <= 14 and j <= 14 and playing_board[x][j] == color and playing_board[x + 1][j + 1] == color and \
                        playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color and \
                        playing_board[x + 4][j + 4] == color:
                    return 1  # Found 5 in a row diagonally down and to the right
                elif x >= 4 and j <= 14 and playing_board[x][j] == color and playing_board[x - 1][j + 1] == color and \
                        playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color and \
                        playing_board[x - 4][j + 4] == color:
                    return 1  # Found 5 in a row diagonally up and to the right
        return 0  # Couldn't find 5 in a row
    else:
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for j in range(ranges["y1"], ranges["y2"] + 1):
                if x <= 14 and playing_board[x][j] == color and playing_board[x + 1][j] == color and \
                        playing_board[x + 2][j] == color and playing_board[x + 3][j] == color and \
                        playing_board[x + 4][j] == color:
                    return 1  # Found 5 in a row vertically
                elif j <= 14 and playing_board[x][j] == color and playing_board[x][j + 1] == color and \
                        playing_board[x][j + 2] == color and playing_board[x][j + 3] == color and \
                        playing_board[x][j + 4] == color:
                    return 1  # Found 5 in a row horizontally
                elif x <= 14 and j <= 14 and playing_board[x][j] == color and playing_board[x + 1][j + 1] == color and \
                        playing_board[x + 2][j + 2] == color and playing_board[x + 3][j + 3] == color and \
                        playing_board[x + 4][j + 4] == color:
                    return 1  # Found 5 in a row diagonally down and to the right
                elif x >= 4 and j <= 14 and playing_board[x][j] == color and playing_board[x - 1][j + 1] == color and \
                        playing_board[x - 2][j + 2] == color and playing_board[x - 3][j + 3] == color and \
                        playing_board[x - 4][j + 4] == color:
                    return 1  # Found 5 in a row diagonally up and to the right
        return 0  # Couldn't find 5 in a row


def count_open_threes(playing_board, color, ranges):
    count = 0
    if ranges is None:
        for x in range(len(playing_board)):
            for y in range(len(playing_board[0])):
                # Check for sequence in horizontal direction
                if y < 15 and playing_board[x][y] == '.' and playing_board[x][y + 1] == color and \
                        playing_board[x][y + 2] == color and playing_board[x][y + 3] == color and \
                        playing_board[x][y + 4] == '.':
                    count += 1
                # Check for sequence in vertical direction
                if x < 15 and playing_board[x][y] == '.' and playing_board[x + 1][y] == color and \
                        playing_board[x + 2][y] == color and playing_board[x + 3][y] == color and \
                        playing_board[x + 4][y] == '.':
                    count += 1
                # Check for sequence in diagonal direction (top-left to bottom-right)
                if x < 15 and y < 15 and playing_board[x][y] == '.' and playing_board[x + 1][y + 1] == color and \
                        playing_board[x + 2][y + 2] == color and playing_board[x + 3][y + 3] == color and \
                        playing_board[x + 4][y + 4] == '.':
                    count += 1
                # Check for sequence in diagonal direction (bottom-left to top-right)
                if x > 3 and y < 15 and playing_board[x][y] == '.' and playing_board[x - 1][y + 1] == color and \
                        playing_board[x - 2][y + 2] == color and playing_board[x - 3][y + 3] == color and \
                        playing_board[x - 4][y + 4] == '.':
                    count += 1
        return count
    else:
        for x in range(ranges["x1"], ranges["x2"] + 1):
            for y in range(ranges["y1"], ranges["y2"] + 1):
                # Check for sequence in horizontal direction
                if y < 15 and playing_board[x][y] == '.' and playing_board[x][y + 1] == color and \
                        playing_board[x][y + 2] == color and playing_board[x][y + 3] == color and \
                        playing_board[x][y + 4] == '.':
                    count += 1
                # Check for sequence in vertical direction
                if x < 15 and playing_board[x][y] == '.' and playing_board[x + 1][y] == color and \
                        playing_board[x + 2][y] == color and playing_board[x + 3][y] == color and \
                        playing_board[x + 4][y] == '.':
                    count += 1
                # Check for sequence in diagonal direction (top-left to bottom-right)
                if x < 15 and y < 15 and playing_board[x][y] == '.' and playing_board[x + 1][y + 1] == color and \
                        playing_board[x + 2][y + 2] == color and playing_board[x + 3][y + 3] == color and \
                        playing_board[x + 4][y + 4] == '.':
                    count += 1
                # Check for sequence in diagonal direction (bottom-left to top-right)
                if x > 3 and y < 15 and playing_board[x][y] == '.' and playing_board[x - 1][y + 1] == color and \
                        playing_board[x - 2][y + 2] == color and playing_board[x - 3][y + 3] == color and \
                        playing_board[x - 4][y + 4] == '.':
                    count += 1
        return count


def evaluate(playing_board, p, ranges):
    score = 0
    o = 'b' if p == 'w' else 'w'
    if max_depth == 1:
        ranges = None

    num_player_win = check_five_in_a_row(playing_board, p, ranges)
    score += num_player_win * 12500

    num_opponent_win = check_five_in_a_row(playing_board, o, ranges)
    score -= num_opponent_win * 12500

    # Add score for number of p's pieces on the playing_board
    num_player_pieces = count_pieces(playing_board, p, ranges)
    score += num_player_pieces * 50

    # Subtract score for number of o's pieces on the playing_board
    num_opponent_pieces = count_pieces(playing_board, o, ranges)
    score -= num_opponent_pieces * 50

    # Add score for potential captures
    num_player_potential_captures = get_num_potential_captures(playing_board, p, ranges)
    score += num_player_potential_captures * 1000

    # Add score for potential captures
    num_opponent_potential_captures = get_num_potential_captures(playing_board, o, ranges)
    score -= num_opponent_potential_captures * 1000

    # Add score for number of potential captures p has
    num_player_captures = get_num_captures(playing_board, p, ranges)
    score += num_player_captures * 2000

    # Subtract score for number of potential captures o has
    num_opponent_captures = get_num_captures(playing_board, o, ranges)
    score -= num_opponent_captures * 2000

    # Add score for number of p's pieces forming open-ended fours
    num_player_open_fours = count_open_fours(playing_board, p, ranges)
    score += num_player_open_fours * 8000

    # Add score for number of p's pieces forming closed fours
    num_player_closed_fours = count_closed_fours(playing_board, p, ranges)
    score += num_player_closed_fours * 4000

    # Subtract score for number of o's pieces forming open-ended fours
    num_opponent_open_fours = count_open_fours(playing_board, o, ranges)
    score -= num_opponent_open_fours * 8000

    # Subtract score for number of o's pieces forming closed fours
    num_opponent_closed_fours = count_closed_fours(playing_board, o, ranges)
    score -= num_opponent_closed_fours * 4000

    # Add score for number of p's pieces forming open-ended threes
    num_player_open_threes = count_open_threes(playing_board, p, ranges)
    score += num_player_open_threes * 2500

    # Add score for number of p's pieces forming closed threes
    num_player_closed_threes = count_closed_threes(playing_board, p, ranges)
    score += num_player_closed_threes * 1000

    # Subtract score for number of o's pieces forming open-ended threes
    num_opponent_open_threes = count_open_threes(playing_board, o, ranges)
    score -= num_opponent_open_threes * 2500

    # Subtract score for number of o's pieces forming closed threes
    num_opponent_closed_threes = count_closed_threes(playing_board, o, ranges)
    score -= num_opponent_closed_threes * 1000

    # Add score for two connect for p
    num_player_open_two_connect = count_two_connect(playing_board, p, ranges)
    score += num_player_open_two_connect * 350

    # Subtract score for two connect for o
    num_opponent_open_two_connect = count_two_connect(playing_board, o, ranges)
    score -= num_opponent_open_two_connect * 350

    return score


def alpha_beta(playing_board, pm, depth, alpha, beta, ranges):
    # check if the game is over or the maximum search depth has been reached
    if depth == 0:
        return evaluate(playing_board, pm, ranges)

    # determine whether the current pm is maximizing or minimizing
    if pm == player:
        # initialize the best score to negative infinity
        best_score = -math.inf

        # iterate through all possible moves
        for move in get_moves(playing_board):
            # make a copy of the playing_board and make the move
            new_board = copy.deepcopy(playing_board)
            new_board = make_move(new_board, pm, move)

            # recursively call the alpha-beta function on the new playing_board with the opposing pm as the current pm
            score = alpha_beta(new_board, opponent, depth - 1, alpha, beta, ranges)

            # update the best score and alpha if the current score is better than the current best score
            if score > best_score:
                best_score = score
                alpha = max(alpha, best_score)

            # check if pruning is possible and return early if it is
            if beta <= alpha:
                break

        return best_score

    else:
        # initialize the best score to positive infinity
        best_score = math.inf

        # iterate through all possible moves
        for move in get_moves(playing_board):
            # make a copy of the playing_board and make the move
            new_board = copy.deepcopy(playing_board)
            new_board = make_move(new_board, pm, move)

            # recursively call the alpha-beta function on the new playing_board with the opposing pm as the current pm
            score = alpha_beta(new_board, player, depth - 1, alpha, beta, ranges)

            # update the best score and beta if the current score is better than the current best score
            if score < best_score:
                best_score = score
                beta = min(beta, best_score)

            # check if pruning is possible and return early if it is
            if beta <= alpha:
                break

        return best_score


# find the best move using the findBestMove function
def find_best_move(depth):
    # set initial values of alpha and beta
    alpha = -math.inf
    beta = math.inf
    main_board = copy.deepcopy(board)
    lm_coordinates = None

    # find all valid moves
    valid_moves = get_moves(main_board)

    # if there is only one valid move, return it
    if len(valid_moves) == 1:
        return valid_moves[0]

    if len(valid_moves) == 361:
        return [9, 9]

    if len(valid_moves) == 360 and player == 'b':
        return [10, 9]

    #  if we are black, for initial
    counter = 361 - len(valid_moves)
    if counter == 3 and main_board[10][10] != opponent:
        return [10, 10]
    if counter == 3 and main_board[10][8] != opponent:
        return [10, 8]

    #  adjusting the frame_controller based on piece count
    if counter == 4 or counter == 5:
        frame_controller = 5
    elif counter <= 10 and (counter != 4 or counter != 5):
        frame_controller = 6
    else:
        frame_controller = 7

    if os.path.isfile('playdata.txt'):
        playdata = open('playdata.txt', 'r')
        playdata_list = [previous for previous in playdata.readlines()]
        last_move = playdata_list[-1]
        last_move = [int(x) for x in last_move.split(' ')]
        x1 = max(last_move[0] - frame_controller, 0)
        x2 = min(last_move[0] + frame_controller, 18)
        y1 = max(last_move[1] - frame_controller, 0)
        y2 = min(last_move[1] + frame_controller, 18)
        lm_coordinates = dict(x1=x1, x2=x2, y1=y1, y2=y2)

        if len(playdata_list) == 1 and player == 'w':
            for x in range(7, 10):
                for y in range(7, 12):
                    if main_board[x][y] != opponent:
                        return [6, 9]
            for x in range(9, 12):
                for y in range(7, 12):
                    if main_board[x][y] != opponent:
                        return [12, 9]

        valid_moves = get_moves(main_board, lm_coordinates)

    # initialize best_move to None and best_score to -infinity
    best_move = None
    best_score = -math.inf

    # iterate through each valid move
    for move in valid_moves:
        # create a copy of the playing_board and make the move
        new_board = copy.deepcopy(main_board)
        new_board = make_move(new_board, player, move)

        # call the alpha beta search function with the new playing_board state
        score = alpha_beta(new_board, player, depth - 1, alpha, beta, lm_coordinates)

        # if the score is greater than the current best score, update best_move and best_score
        if score > best_score:
            best_move = move
            best_score = score

    if best_score <= 300:
        random_list = []
        for x in range(7, 13):
            for y in range(7, 13):
                if get_colour(main_board, x, y) == '.':
                    random_list.append([x, y])
        if [7, 9] in random_list:
            return [7, 9]
        if [8, 9] in random_list:
            return [8, 9]
        return random.choice(random_list)

    return best_move


# write the output to the output.txt file
start = time.time()
write_output(find_best_move(max_depth))
end = time.time()

print(end - start)
