import random
import numpy as np


class P1:
    def __init__(self, board, available_pieces):
        self.pieces = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)]  # All 16 pieces
        self.board = np.array(board)
        self.available_pieces = available_pieces

    def select_piece(self):

        remaining_pieces = len(self.available_pieces)

        if len(self.available_pieces) >= 13:
            return random.choice(self.available_pieces)
        elif remaining_pieces >= 9:
            depth = 8
        else:
            depth = 16

        best_piece = None
        best_score = -float('inf')

        for piece in self.available_pieces:
            score = self.minimax(self.board, piece, True, depth)  # 깊이를 제한
            if score > best_score:
                best_score = score
                best_piece = piece

        return best_piece

    def minimax(self, board, piece, is_maximizing_player, depth, alpha=-float('inf'), beta=float('inf')):
        available_moves = self.get_available_moves(board)

        # 남은 수가 적거나 깊이가 낮을 때 가지치기 없이 전체 탐색
        if len(available_moves) <= 6 or depth <= 2:
            return self.full_search_minimax(board, piece, is_maximizing_player, depth)

        if depth == 0 or self.is_game_over(board):
            return self.evaluate(board)

        if is_maximizing_player:
            max_score = -float('inf')

            for move in available_moves:
                simulated_board = self.simulate_move(board, piece, move)
                score = self.minimax(simulated_board, piece, False, depth - 1, alpha, beta)
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)

                if beta <= alpha:  # 가지치기
                    break
            return max_score
        else:
            min_score = float('inf')
            opponent_pieces = [p for p in self.pieces if p != piece]

            for move in available_moves:
                opponent_piece = random.choice(opponent_pieces)
                simulated_board = self.simulate_move(board, opponent_piece, move)
                score = self.minimax(simulated_board, piece, True, depth - 1, alpha, beta)
                min_score = min(min_score, score)
                beta = min(beta, min_score)

                if beta <= alpha:  # 가지치기
                    break
            return min_score

    def full_search_minimax(self, board, piece, is_maximizing_player, depth):
        """가지치기 없이 모든 경우를 탐색하는 Minimax"""
        if depth == 0 or self.is_game_over(board):
            return self.evaluate(board)

        available_moves = self.get_available_moves(board)
        if is_maximizing_player:
            max_score = -float('inf')

            for move in available_moves:
                simulated_board = self.simulate_move(board, piece, move)
                score = self.full_search_minimax(simulated_board, piece, False, depth - 1)
                max_score = max(max_score, score)
            return max_score
        else:
            min_score = float('inf')
            opponent_pieces = [p for p in self.pieces if p != piece]

            for move in available_moves:
                opponent_piece = random.choice(opponent_pieces)
                simulated_board = self.simulate_move(board, opponent_piece, move)
                score = self.full_search_minimax(simulated_board, piece, True, depth - 1)
                min_score = min(min_score, score)
            return min_score

    def evaluate(self, board):
        if self.check_win(board):
            return 3
        elif self.is_board_full(board):
            return 2
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
        remaining_moves = len(available_moves)

        # 먼저 승리 가능한 곳에 말 두기
        for row, col in available_moves:
            win_move = self.check_win_in_line(row, col, selected_piece)
            if win_move:
                return win_move

            win_move_square = self.check_win_in_square(row, col, selected_piece)
            if win_move_square:
                return win_move_square

        if remaining_moves >= 14:
            return random.choice(available_moves)
        elif remaining_moves == 12:
            depth = 6
        else:
            depth = 16

        best_move = None
        best_score = -float('inf')

        for move in available_moves:
            simulated_board = self.simulate_move(self.board, selected_piece, move)
            score = self.minimax(simulated_board, selected_piece, False, depth)
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

    def check_win_in_line(self, row, col, selected_piece):
        # 가로, 세로, 대각선에서 승리할 수 있는지 체크
        possible_lines = [
            [(row, i) for i in range(4)],  # 가로
            [(i, col) for i in range(4)],  # 세로
            [(i, i) for i in range(4)],  # 대각선
            [(i, 3-i) for i in range(4)],  # 반대 대각선
        ]
        selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4 = selected_piece

        for line in possible_lines:
            empty_count = 0
            matching_count = 0  # 선택된 말과 속성이 일치하는 말의 수
            for r, c in line:
                if self.board[r, c] == 0:
                    empty_count += 1
                else:
                    # 보드에 있는 말의 속성 비교 (속성1, 속성2, 속성3, 속성4)
                    piece = self.pieces[self.board[r, c] - 1]  # 1-based indexing
                    piece_attribute1, piece_attribute2, piece_attribute3, piece_attribute4 = piece

                    # selected_piece와 속성 값 중 하나라도 일치하는지 확인
                    if (piece_attribute1 == selected_attribute1 or
                        piece_attribute2 == selected_attribute2 or
                        piece_attribute3 == selected_attribute3 or
                        piece_attribute4 == selected_attribute4):
                        matching_count += 1

            # 3개의 선택된 말과 1개의 빈 칸이 있으면 승리할 수 있음
            if empty_count == 1 and matching_count == 3:
                return (row, col)

        return None

    def check_win_in_square(self, row, col, selected_piece):
        # 2x2 정사각형에서 승리할 수 있는지 체크
        if row < 3 and col < 3:  # 2x2 정사각형이 존재할 수 있는 범위
            square_positions = [
                [(row, col), (row, col+1), (row+1, col), (row+1, col+1)]
            ]
            selected_attribute1, selected_attribute2, selected_attribute3, selected_attribute4 = selected_piece

            for square in square_positions:
                empty_count = 0
                matching_count = 0  # 선택된 말과 속성이 일치하는 말의 수
                for r, c in square:
                    if self.board[r, c] == 0:
                        empty_count += 1
                    else:
                        # 보드에 있는 말의 속성 비교 (속성1, 속성2, 속성3, 속성4)
                        piece = self.pieces[self.board[r, c] - 1]  # 1-based indexing
                        piece_attribute1, piece_attribute2, piece_attribute3, piece_attribute4 = piece

                        # selected_piece와 속성 값 중 하나라도 일치하는지 확인
                        if (piece_attribute1 == selected_attribute1 or
                            piece_attribute2 == selected_attribute2 or
                            piece_attribute3 == selected_attribute3 or
                            piece_attribute4 == selected_attribute4):
                            matching_count += 1

                # 3개의 선택된 말과 1개의 빈 칸이 있으면 승리할 수 있음
                if empty_count == 1 and matching_count == 3:
                    return (row, col)

        return None