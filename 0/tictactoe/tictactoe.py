"""
Tic Tac Toe AI
"""

import math
import copy
import random


X = "X"
O = "O"
EMPTY = None

# 4 optimum first moves for x to randomly choose from
# (it always calculates one of these using minimax so this is to save time)
FIRST_X_MOVES = [(0,0), (0,2), (2,0), (2,2)]


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_moves = 0
    o_moves = 0
    for row in board:
        for i in row:
            if i == O: o_moves += 1
            if i == X: x_moves += 1
    if x_moves > o_moves:
        return O
    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    all_possible_actions = set()
    for row_index, row in enumerate(board, start=0):
        for box_index, box in enumerate(row, start=0):
            if box == EMPTY:
                all_possible_actions.add((row_index, box_index))
    return(all_possible_actions)


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    row = action[0]
    column = action[1]
    new_board = copy.deepcopy(board)
    if new_board[row][column] != EMPTY:
        raise Exception("not valid move")
    new_board[row][column] = player(new_board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    Returns None if tie or the game is in progress.
    """
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return row[0]
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    for row in board:
        for i in row:
            if i == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    the_winner = winner(board=board)
    if the_winner == O: return -1
    if the_winner == X: return 1
    return 0


def max_value(board):
    """
    Max function of minimax algorithm. 
    """
    if terminal(board):
        return utility(board)
    v = -2
    for action in actions(board):
        min_v = min_value(result(board=board, action=action))
        v = max(v, min_v)
        if v == 1:
            return v
    return v


def min_value(board):
    """
    Min function of minimax algorithm. 
    """
    if terminal(board):
        return utility(board)
    v = 2
    alpha = None
    for action in actions(board):
        max_v = max_value(result(board=board, action=action))
        v = min(v, max_v)
        if v == -1:
            return v
    return v


def minimax(board):
    """
    Returns best move where other side plays optimally.
    """
    if terminal(board):
        return None

    if player(board) == X:
        if board == initial_state():
            return FIRST_X_MOVES[random.randint(0,3)]
        best_action = None
        best_v = -2
        for action in actions(board):
            v = min_value(result(board=board, action=action))
            if v > best_v:
                best_v = v
                best_action = action
        return best_action

    elif player(board) == O:
        best_action = None
        best_v = 2
        for action in actions(board):
            v = max_value(result(board=board, action=action))
            if v < best_v:
                best_v = v
                best_action = action
        return best_action
