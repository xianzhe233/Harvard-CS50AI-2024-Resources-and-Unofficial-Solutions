from tictactoe import *

def print_board(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            c = board[i][j]
            if c == None:
                c = '_'
            print(c, end=" ")
        print("")
		
def test_initial_state():
    print_board(initial_state())
	
def test_player(board):
    print_board(board)
    print(player(board))
	
def test_actions(board):
    print_board(board)
    print(actions(board))
	
def test_result(board, action):
    print_board(result(board, action))

if __name__ == "__main__":
	board = [[X, EMPTY, EMPTY],
            [O, O, O],
            [EMPTY, EMPTY, EMPTY]]
	print(terminal(board))
	board = [[X, X, X],
            [EMPTY, O, EMPTY],
            [EMPTY, EMPTY, EMPTY]]
	print(utility(board))
	board = [[O, X, O],
            [O, X, O],
            [X, O, X]]
	print(utility(board))