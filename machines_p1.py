import random
import numpy as np

class P1:
    def __init__(self, board, available_pieces):
        self.pieces = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)]
        self.board = np.array(board)
        self.available_pieces = available_pieces

    def select_piece(self):
        if len(self.available_pieces)  >= 13:
            return random.choice(self.available_pieces)

        best_piece = None
        best_score = -float('inf')

        for piece in self.available_pieces:
            score = self.minimax(self.board, piece, True, 4)  # 깊이를  제한
            if score > best_score:
                best_score = score
                best_piece = piece

        return best_piece

    def minimax(self, board, piece, is_maximizing_player, depth):
        if depth == 0 or self.is_game_over(board):
            return self.evaluate(board)

        if is_maximizing_player:
            max_score = -float('inf')
            available_moves = self.get_available_moves(board)

            for move in available_moves:
                simulated_board = self.simulate_move(board, piece, move)
                score = self.minimax(simulated_board, piece, False, depth - 1)
                max_score = max(max_score, score)
            return max_score
        else:
            min_score = float('inf')
            opponent_pieces = [p for p in self.pieces if p != piece]
            available_moves = self.get_available_moves(board)

            for move in available_moves:
                opponent_piece = random.choice(opponent_pieces)
                simulated_board = self.simulate_move(board, opponent_piece, move)
                score = self.minimax(simulated_board, piece, True, depth - 1)
                min_score = min(min_score, score)
            return min_score

    def evaluate(self, board):
        if self.check_win(board):
            return 1
        elif self.is_board_full(board):
            return 0
        return -1

    def get_available_moves(self, board):
        return list(zip(*np.where(board == 0)))

    def simulate_move(self, board, piece, move):
        simulated_board = board.copy()
        row, col = move
        piece_idx = self.pieces.index(piece) + 1
        simulated_board[row, col] = piece_idx
        return simulated_board

    def place_piece(self, selected_piece):
        available_moves = self.get_available_moves(self.board)

        if len(available_moves) >= 14:
            return random.choice(available_moves)

        best_move = None
        best_score = -float('inf')

        for move in available_moves:
            simulated_board = self.simulate_move(self.board, selected_piece, move)
            score = self.minimax(simulated_board, selected_piece, False, 4)  # 깊이를 제한
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def is_game_over(self, board):
        return self.check_win(board) or self.is_board_full(board)

    def check_win(self, board):
        for i in range(4):
            if self.check_line(board[i, :]) or self.check_line(board[:, i]):
                return True
        if self.check_line(np.diag(board)) or self.check_line(np.diag(np.fliplr(board))):
            return True
        return False

    def check_line(self, line):
        if 0 in line:
            return False
        characteristics = np.array([self.pieces[idx - 1] for idx in line])
        return np.any(np.all(characteristics == characteristics[0], axis=0))

    def is_board_full(self, board):
        return np.all(board != 0)