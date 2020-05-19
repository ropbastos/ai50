"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


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
    # Counts moves on board to determine number of turns elapsed.
    turns = 0
    for row in board:
        for position in row:
            if position is not EMPTY:
                turns += 1
   
    # X plays even turns, O plays odd turns
    return X if turns % 2 == 0 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = []
    i, j = -1, -1
    for row in board:
        i += 1
        for position in row:
            j = (j + 1) % 3
            if position is EMPTY:
                actions.append((i,j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    result = copy.deepcopy(board)
    if result[i][j] is EMPTY:
        result[i][j] = player(board)
        return result
    else:
        raise IndexError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check for rows
    if board[0][0] != EMPTY and board[0][0] == board[0][1] == board[0][2]:
        return board[0][0] 
    elif board[1][0] != EMPTY and board[1][0] == board[1][1] == board[1][2]:
        return board[1][0]
    elif board[2][0] != EMPTY and  board[2][0] == board[2][1] == board[2][2]:
        return board[2][0]

    # Check for columns
    if board[0][0] != EMPTY and board[0][0] == board[1][0] == board[2][0]:
        return board[0][0] 
    elif board[0][1] != EMPTY and board[0][1] == board[1][1] == board[2][1]:
        return board[0][1]
    elif board[0][2] != EMPTY and board[0][2] == board[1][2] == board[2][2]:
        return board[0][2]

    # Check for diagonals
    if board[0][0] != EMPTY and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0] 
    elif board[0][2] != EMPTY and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2] 

    # No winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    else:
        for row in board:
            for position in row:
                if position is EMPTY:
                    return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    won = winner(board)
    if won == X:
        return 1
    elif won == O:
        return -1
    else:
        return 0


def max_value(board, alpha, beta):
    """
    Returns maximum value that can be guaranteed playing from given state.
    """
    if terminal(board):
        return utility(board)
    else:
        value = float('-inf')
        for action in actions(board):
            value = max(value, min_value(result(board, action), alpha, beta))
            alpha = max(alpha, value)
            if value > beta:
                break
        return value


def min_value(board, alpha, beta):
    """
    Returns minimum value that can be guaranteed playing from given state.
    """
    if terminal(board):
        return utility(board)
    else:
        value = float('inf')
        for action in actions(board):
            value = min(value, max_value(result(board, action), alpha, beta))
            beta = min(beta, value)
            if value < alpha:
                break
        return value


def is_empty(board):
    """
    Checks if board is empty.
    """
    for row in board:
        for position in row:
            if position is not EMPTY:
                return False
    return True


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Alpha-beta pruning
    alpha = float('-inf')
    beta = float('inf')

    # MAX
    if player(board) == X:
        # Plays center quickly if first move.
        if is_empty(board):
            return (1,1)
        highest_value = float('-inf')
        for action in actions(board):
            action_value = min_value(result(board, action), alpha, beta)
            if action_value > highest_value:
                chosen_action = action
                highest_value = action_value
    # MIN
    else:
        lowest_value = float('inf')
        for action in actions(board):
            action_value = max_value(result(board, action), alpha, beta)
            if action_value < lowest_value:
                chosen_action = action
                lowest_value = action_value
    
    return chosen_action


              

