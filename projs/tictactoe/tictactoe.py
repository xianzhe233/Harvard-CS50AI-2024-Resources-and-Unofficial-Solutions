"""
Tic Tac Toe Player
"""

from ast import Name
import math
import copy
from tkinter import NO

X = "X"
O = "O"
EMPTY = None
INF = 100


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
    
    def count_markers(marker):
        return sum(row.count(marker) for row in board)
    
    if count_markers(X) == count_markers(O):
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    
    def find_empty_pos():
        return set((i, j) for i in range(len(board)) for j in range(len(board[0])) if board[i][j] == EMPTY)
    
    return find_empty_pos()


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    
    def verify_action():
        x, y = action
        if x < 0 or y < 0 or x >= len(board) or y >= len(board[0]) or board[x][y] != EMPTY:
            raise NameError("Invalid action")
        else:
            return x, y

    new_board = copy.deepcopy(board)
    x, y = verify_action()
    new_board[x][y] = player(board)
    
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    def check_line(line, marker):
        return all(item == marker for item in line)
        
    def check_win(marker):
        # check rows
        if any(check_line(row, marker) for row in board):
            return True
        # check columns
        if any(check_line(col, marker) for col in zip(*board)):
            return True
        
        diagonals = [
            [board[0][0], board[1][1], board[2][2]],
            [board[0][2], board[1][1], board[2][0]]
        ]
        # check diagonals
        if any(check_line(diagonal, marker) for diagonal in diagonals):
            return True

        # no winner
        return None
    
    if check_win(X):
        return X
    elif check_win(O):
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    def exist_empty():
        return any(EMPTY in row for row in board)

    return not (exist_empty() and winner(board) == None)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    res = winner(board)
    if res == X:
        return 1
    elif res == O:
        return -1
    else:
        return 0
    

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    def max_value(board, alpha, beta):
        if terminal(board):
            return utility(board)

        best = -INF
        for action in actions(board):
            best = max(best, min_value(result(board, action), alpha, beta))
            if best >= beta:
                return best
            alpha = max(alpha, best)
        return best

    def min_value(board, alpha, beta):
        if terminal(board):
            return utility(board)

        best = INF
        for action in actions(board):
            best = min(best, max_value(result(board, action), alpha, beta))
            if best <= alpha:
                return best
            beta = min(beta, best)
        return best

    if terminal(board):
        return None

    current_player = player(board)
    alpha = -INF
    beta = INF

    best_action = None
    if current_player == X:
        best_value = -INF
        for action in actions(board):
            value = min_value(result(board, action), alpha, beta)
            if value > best_value:
                best_value = value
                best_action = action
            alpha = max(alpha, best_value)
    else:
        best_value = INF
        for action in actions(board):
            value = max_value(result(board, action), alpha, beta)
            if value < best_value:
                best_value = value
                best_action = action
            beta = min(beta, best_value)

    return best_action