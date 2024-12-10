import numpy as np
from itertools import product
import random
import copy

# 보드 크기 및 상수 정의
BOARD_ROWS = 4
BOARD_COLS = 4
WIN_SCORE = 10
CENTER_WEIGHT = 5
THREAT_PENALTY = 10
SIMULATION_COUNT = 100


class P1:
    def __init__(self, board, available_pieces):
        self.pieces = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)]
        self.board = board
        self.available_pieces = available_pieces
        self.center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    def evaluate_piece_for_opponent(self, piece):
        lose_score = 0
        gain_score = 0

        for _ in range(SIMULATION_COUNT):
            simulated_board = copy.deepcopy(self.board)
            available_locations = copy.deepcopy(self.get_available_locations())
            simulated_piece = copy.deepcopy(piece)

            for row, col in available_locations:
                simulated_board[row][col] = self.pieces.index(simulated_piece) + 1

                if self.check_win(simulated_board):
                    lose_score += WIN_SCORE

                lose_score += self.evaluate_threat(simulated_board)

                for my_row, my_col in self.get_available_locations():
                    my_simulated_board = copy.deepcopy(simulated_board)
                    my_simulated_board[my_row][my_col] = self.pieces.index(simulated_piece) + 1
                    if self.check_win(my_simulated_board):
                        gain_score -= WIN_SCORE

        return lose_score - gain_score

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

        if (row, col) in self.center_positions:
            score += CENTER_WEIGHT

        if self.check_win(simulated_board):
            score += WIN_SCORE

        score -= self.evaluate_threat(simulated_board)
        return score

    def place_piece(self, selected_piece):
        if self.is_first_move():
            for row, col in self.center_positions:
                if self.board[row][col] == 0:
                    return row, col

        best_positions = []
        max_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        for row, col in self.get_available_locations():
            score = self.evaluate_position_control(row, col, selected_piece)

            if score > max_score:
                max_score = score
                best_positions = [(row, col)]
            elif score == max_score:
                best_positions.append((row, col))

            alpha = max(alpha, score)
            if beta <= alpha:
                break

        return random.choice(best_positions)

    def is_first_move(self):
        return np.count_nonzero(self.board) == 0

    def get_available_locations(self):
        return [(row, col) for row, col in product(range(BOARD_ROWS), range(BOARD_COLS)) if self.board[row][col] == 0]

    def simulate_board(self, row, col, piece):
        simulated_board = np.copy(self.board)
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

        def check_square():
            for i in range(BOARD_ROWS - 1):
                for j in range(BOARD_COLS - 1):
                    square = [
                        board[i][j], board[i][j + 1],
                        board[i + 1][j], board[i + 1][j + 1]
                    ]
                    if 0 not in square:
                        characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in square])
                        for k in range(4):
                            if len(set(characteristics[:, k])) == 1:
                                return True
            return False

        for col in range(BOARD_COLS):
            if check_line([board[row][col] for row in range(BOARD_ROWS)]):
                return True
        for row in range(BOARD_ROWS):
            if check_line([board[row][col] for col in range(BOARD_COLS)]):
                return True
        if check_line([board[i][i] for i in range(BOARD_ROWS)]) or check_line([board[i][BOARD_ROWS - i - 1] for i in range(BOARD_ROWS)]):
            return True

        return check_square()

    def evaluate_threat(self, board):
        def check_line_threat(line):
            filled_positions = [piece for piece in line if piece != 0]
            if len(filled_positions) == 3:
                characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in filled_positions])
                for i in range(4):
                    if len(set(characteristics[:, i])) == 1:
                        return THREAT_PENALTY
            return 0

        def check_square_threat():
            for i in range(BOARD_ROWS - 1):
                for j in range(BOARD_COLS - 1):
                    square = [
                        board[i][j], board[i][j + 1],
                        board[i + 1][j], board[i + 1][j + 1]
                    ]
                    filled_positions = [piece for piece in square if piece != 0]
                    if len(filled_positions) == 3:
                        characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in filled_positions])
                        for k in range(4):
                            if len(set(characteristics[:, k])) == 1:
                                return THREAT_PENALTY
            return 0

        for col in range(BOARD_COLS):
            if check_line_threat([board[row][col] for row in range(BOARD_ROWS)]):
                return THREAT_PENALTY
        for row in range(BOARD_ROWS):
            if check_line_threat([board[row][col] for col in range(BOARD_COLS)]):
                return THREAT_PENALTY
        if check_line_threat([board[i][i] for i in range(BOARD_ROWS)]) or check_line_threat([board[i][BOARD_ROWS - i - 1] for i in range(BOARD_ROWS)]):
            return THREAT_PENALTY

        return check_square_threat()
