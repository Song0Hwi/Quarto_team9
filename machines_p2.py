import numpy as np
from itertools import product

class P2():
    def __init__(self, board, available_pieces):
        self.pieces = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)]
        self.board = board
        self.available_pieces = available_pieces

    def evaluate_piece_for_opponent(self, piece):
        score = 0
        for row, col in self.get_available_locations():
            simulated_board = self.simulate_board(row, col, piece)
            if self.check_win(simulated_board):
                score += 10
            score += self.evaluate_opponent_threat(simulated_board, piece)
        return score

    def select_piece(self):
        best_piece = None
        min_score = float('inf')
        for piece in self.available_pieces:
            score = self.evaluate_piece_for_opponent(piece)
            if score < min_score:
                min_score = score
                best_piece = piece
        return best_piece

    def evaluate_position_control(self, row, col, piece):
        score = 0
        simulated_board = self.simulate_board(row, col, piece)
        if self.check_win(simulated_board):
            score += 10
        score += self.evaluate_self_threat(simulated_board, piece)
        return score

    def place_piece(self, selected_piece):
        best_position = None
        max_score = -float('inf')
        for row, col in self.get_available_locations():
            score = self.evaluate_position_control(row, col, selected_piece)
            if score > max_score:
                max_score = score
                best_position = (row, col)
        return best_position

    def get_available_locations(self):
        return [(row, col) for row, col in product(range(4), range(4)) if self.board[row][col] == 0]

    def simulate_board(self, row, col, piece):
        simulated_board = self.board.copy()
        simulated_board[row][col] = self.pieces.index(piece) + 1
        return simulated_board

    def check_win(self, board):
        def check_line(line):
            if 0 in line:
                return False
            characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in line])
            for i in range(4):
                if len(set(characteristics[:, i])) == 1:
                    return True
            return False

        for col in range(4):
            if check_line([board[row][col] for row in range(4)]):
                return True

        for row in range(4):
            if check_line([board[row][col] for col in range(4)]):
                return True

        if check_line([board[i][i] for i in range(4)]) or check_line([board[i][3 - i] for i in range(4)]):
            return True

        for r in range(3):
            for c in range(3):
                subgrid = [board[r][c], board[r][c + 1], board[r + 1][c], board[r + 1][c + 1]]
                if 0 not in subgrid:
                    characteristics = [self.pieces[idx - 1] for idx in subgrid]
                    for i in range(4):
                        if len(set(char[i] for char in characteristics)) == 1:
                            return True
        return False

    def evaluate_opponent_threat(self, board, piece):
        return 0

    def evaluate_self_threat(self, board, piece):
        return 0
