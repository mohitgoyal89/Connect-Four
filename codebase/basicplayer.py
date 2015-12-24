from util import memoize, run_search_function
import sys
from connectfour import ConnectFourRunner


def basic_evaluate(board):
    """
    The original focused-evaluate function from the lab.
    The original is kept because the lab expects the code in the lab to be modified. 
    """
    if board.is_game_over():
        # If the game has been won, we know that it must have been
        # won or ended by the previous move.
        # The previous move was made by our opponent.
        # Therefore, we can't have won, so return -1000.
        # (note that this causes a tie to be treated like a loss)
        score = -1000
    else:
        score = board.longest_chain(board.get_current_player_id()) * 10
        # Prefer having your pieces in the center of the board.
        for row in range(6):
            for col in range(7):
                if board.get_cell(row, col) == board.get_current_player_id():
                    score -= abs(3 - col)
                elif board.get_cell(row, col) == board.get_other_player_id():
                    score += abs(3 - col)

    return score


# new_evaluate implements a better evaluation function which computes the number of winning positions
# in the board and add it to spatial distribution function result for given board state for a non terminal node
# In this winning count is calculated for both player and opponent.
def new_evaluate(board):
    if board.is_game_over():
        return -1000
    else:
        winCount = 0
        lossCount = 0
        minDis = board.longest_chain(board.get_current_player_id()) * 10
        for row in xrange(0, 6):
            for col in xrange(0, 7):
                if board.get_cell(row, col) == board.get_current_player_id():
                    winCount += board.getWinningRowCount(row, col, board.get_current_player_id())
                    minDis -= abs(3 - col)

                elif board.get_cell(row, col) == board.get_other_player_id():
                    lossCount += board.getWinningRowCount(row, col, board.get_other_player_id())
                    minDis += abs(3 - col)

        return (winCount - lossCount) + minDis


def get_all_next_moves(board):
    """ Return a generator of all moves that the current player could take from this position """
    from connectfour import InvalidMoveException

    for i in xrange(board.board_width):
        try:
            yield (i, board.do_move(i))
        except InvalidMoveException:
            pass


def is_terminal(depth, board):
    """
    Generic terminal state check, true when maximum depth is reached or
    the game has ended.
    """
    return depth <= 0 or board.is_game_over()


# Implemented minimax algorithm which computes the max value for current player
# At depth 4 utility value is calculated for non terminal nodes and returned
# It return the column number of the most favourable move for the current player
def minimax(board, depth, eval_fn=basic_evaluate,
            get_next_moves_fn=get_all_next_moves,
            is_terminal_fn=is_terminal,
            verbose=True):
    maxValue = -sys.maxint
    columnIndex = 0
    if eval_fn == basic_evaluate:
        ConnectFourRunner.bpNodesExpanded += 1
    if eval_fn == new_evaluate:
        ConnectFourRunner.npNodesExpanded += 1
    for move, nextBoard in get_next_moves_fn(board):
        nextMoveRes = minimax_helper(nextBoard, depth - 1, False, eval_fn)
        if nextMoveRes > maxValue:
            maxValue = nextMoveRes
            columnIndex = move
    return columnIndex


# This is a helper function that recursively calls itself
# This function is called by current player who is Max node.
# This function return max/ min values depending upon the isMax boolean flag is set or not
def minimax_helper(board, depth, isMax, eval_fn=basic_evaluate,
                   get_next_moves_fn=get_all_next_moves,
                   is_terminal_fn=is_terminal):
    if eval_fn == basic_evaluate:
        ConnectFourRunner.bpNodesExpanded += 1
    if eval_fn == new_evaluate:
        ConnectFourRunner.npNodesExpanded += 1
    if is_terminal_fn(depth, board):
        return eval_fn(board)
    else:
        if isMax:
            res = - sys.maxint
            for move, nextBoard in get_next_moves_fn(board):
                nextMoveRes = minimax_helper(nextBoard, depth - 1, False, eval_fn)
                if nextMoveRes > res:
                    res = nextMoveRes
            return res
        else:
            res = sys.maxint
            for move, nextBoard in get_next_moves_fn(board):
                nextMoveRes = minimax_helper(nextBoard, depth - 1, True, eval_fn)
                if nextMoveRes < res:
                    res = nextMoveRes
            return res


def rand_select(board):
    """
    Pick a column by random
    """
    import random
    moves = [move for move, new_board in get_all_next_moves(board)]
    return moves[random.randint(0, len(moves) - 1)]


random_player = lambda board: rand_select(board)
basic_player = lambda board: minimax(board, depth=4, eval_fn=basic_evaluate)
new_player = lambda board: minimax(board, depth=4, eval_fn=new_evaluate)
progressive_deepening_player = lambda board: run_search_function(board, search_fn=minimax, eval_fn=basic_evaluate)
