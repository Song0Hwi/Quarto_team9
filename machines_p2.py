import numpy as np
import random
from itertools import product

import time
import copy

BOARD_ROWS = 4
BOARD_COLS = 4


class P2():
    def __init__(self, board, available_pieces):
        self.pieces = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in
                       range(2)]  # All 16 pieces
        self.board = board  # Include piece indices. 0:empty / 1~16:piece
        self.available_pieces = available_pieces  # Currently available pieces in a tuple type (e.g. (1, 0, 1, 0))

    def select_piece(self):
        if (len(self.available_pieces) >= 14):
            return random.choice(self.available_pieces)
        best_score = -1e9
        best_piece = None

        for piece in self.available_pieces:
            new_board = copy.deepcopy(self.board)
            new_pieces = copy.deepcopy(self.available_pieces)
            new_pieces.remove(piece)

            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    if new_board[row][col] == 0:
                        new_board[row][col] = self.pieces.index(piece) + 1
                        for depth in range(1, 5):
                            start_time = time.time()
                            score = self.minimax(new_board, new_pieces, depth, False, -1e9, 1e9)
                            end_time = time.time()

                            if end_time - start_time > 30:
                                break

                        if score > best_score:
                            if score == 1e9:
                                return piece
                            best_score = score
                            best_piece = piece

                        new_board[row][col] = 0

        return best_piece

    def place_piece(self, selected_piece):
        available_locs = [(row, col) for row, col in product(range(4), range(4)) if self.board[row][col] == 0]
        if len(self.available_pieces) >= 13:
            return random.choice(available_locs)
        else:
            best_value = float('-inf')
            best_move = None

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                new_board = copy.deepcopy(self.board)
                if new_board[row][col] == 0:

                    new_board[row][col] = self.pieces.index(selected_piece) + 1
                    for depth in range(1, 5):
                        start_time = time.time()
                        value = self.minimax(new_board, self.available_pieces, depth, True, -1e9, 1e9)
                        end_time = time.time()

                        if end_time - start_time > 30:
                            break

                    if value > best_value:
                        best_value = value
                        best_move = (row, col)
        return best_move[0], best_move[1]

    def minimax(self, board, available_pieces, depth, maximizing_player, alpha, beta):
        if self.check_win():
            return 1e9
        elif depth == 0 or self.is_board_full():
            return 0

        if maximizing_player:
            max_eval = -1e9
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    for piece in available_pieces:
                        if board[row][col] == 0:
                            board[row][col] = self.pieces.index(piece) + 1
                            available_pieces.remove(piece)
                            eval = self.minimax(board, available_pieces, depth - 1, False, alpha, beta)
                            board[row][col] = 0
                            available_pieces.append(piece)
                            max_eval = max(max_eval, eval)
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
            return max_eval
        else:
            min_eval = 1e9
            for row in range(BOARD_ROWS):
                for col in range(BOARD_COLS):
                    for piece in available_pieces:
                        if board[row][col] == 0:
                            board[row][col] = self.pieces.index(piece) + 1
                            available_pieces.remove(piece)
                            eval = self.minimax(board, available_pieces, depth - 1, True, alpha, beta)
                            board[row][col] = 0
                            available_pieces.append(piece)
                            min_eval = min(min_eval, eval)
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
            return min_eval

    def evaluate(self):
        if (self.check_win()):
            return 1e9
        elif (not self.check_win() | self.is_board_full()):
            return -1e9
        else:
            # 각 line, 사각형에서 세 개가 모였을 때, 겹치는 속성이 있는지
            # 즉, 상대방이 다음 차례에 이길 수 있는 상황인지
            # -> -1e9
            if self.check_three():
                return -1e9

            # 가장자리보다 가운데에 말을 둘 때 더 높은 점수를 준다? 별로 필요없는 거 같기는 한데..

            #
            return 100

    def is_board_full(self):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] == 0:
                    return False
        return True

    def check_line(self, line):
        if 0 in line:
            return False  # Incomplete line
        characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in line])
        for i in range(4):  # Check each characteristic (I/E, N/S, T/F, P/J)
            if len(set(characteristics[:, i])) == 1:  # All share the same characteristic
                return True
        return False

    # 한 줄에 세 개 이상 같은 속성이 있는지 체크
    # [self.board[row][col] for row in range(BOARD_ROWS)]
    def check_line_three(self, line):
        if line.count(1) < 3:
            return False
        num_pieces = len(line)
        characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in line])
        for i in range(4):
            if num_pieces >= 3:
                if len(set(characteristics[:, i])) <= 1:
                    return True
        return False

    def check_2x2_subgrid_win(self):
        for r in range(BOARD_ROWS - 1):
            for c in range(BOARD_COLS - 1):
                subgrid = [self.board[r][c], self.board[r][c + 1], self.board[r + 1][c], self.board[r + 1][c + 1]]
                if 0 not in subgrid:  # All cells must be filled
                    characteristics = [self.pieces[idx - 1] for idx in subgrid]
                    for i in range(4):  # Check each characteristic (I/E, N/S, T/F, P/J)
                        if len(set(char[i] for char in characteristics)) == 1:  # All share the same characteristic
                            return True
        return False

    def check_2x2_subgrid_three(self):
        for r in range(BOARD_ROWS - 1):
            for c in range(BOARD_COLS - 1):
                subgrid = [self.board[r][c], self.board[r][c + 1], self.board[r + 1][c], self.board[r + 1][c + 1]]
                count = sum(1 for x in subgrid if x == 1)
                if count >= 3:
                    for i in range(4):
                        if subgrid[i] == 1:
                            characteristics = [self.pieces[subgrid[i] - 1]]
                            for j in range(4):
                                if len(set(char[t] for char in characteristics)) == 1:
                                    return True
        return False

    def check_win(self):
        # Check rows, columns, and diagonals
        for col in range(BOARD_COLS):
            if self.check_line([self.board[row][col] for row in range(BOARD_ROWS)]):
                return True

        for row in range(BOARD_ROWS):
            if self.check_line([self.board[row][col] for col in range(BOARD_COLS)]):
                return True

        if self.check_line([self.board[i][i] for i in range(BOARD_ROWS)]) or self.check_line(
                [self.board[i][BOARD_ROWS - i - 1] for i in range(BOARD_ROWS)]):
            return True

        # Check 2x2 sub-grids
        if self.check_2x2_subgrid_win():
            return True

        return False

    def check_three(self):
        for col in range(BOARD_COLS):
            if self.check_line_three([self.board[row][col] for row in range(BOARD_ROWS)]):
                return True

        for row in range(BOARD_ROWS):
            if self.check_line_three([self.board[row][col] for col in range(BOARD_COLS)]):
                return True

        if self.check_line_three([self.board[i][i] for i in range(BOARD_ROWS)]) or self.check_line(
                [self.board[i][BOARD_ROWS - i - 1] for i in range(BOARD_ROWS)]):
            return True

            # Check 2x2 sub-grids
        if self.check_2x2_subgrid_three():
            return True

        return False