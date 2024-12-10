import numpy as np
from itertools import product
import random

# 보드 크기 및 기타 상수 정의
BOARD_ROWS = 4
BOARD_COLS = 4
WIN_SCORE = 10
CENTER_WEIGHT = 5
THREAT_PENALTY = 10

class P1:
    def __init__(self, board, available_pieces):
        # 기본 게임 데이터 초기화
        self.pieces = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)]
        self.board = board
        self.available_pieces = available_pieces
        self.center_positions = [(2, 2), (2, 3), (3, 2), (3, 3)]

    # 상대방의 가장 최적의 조각을 평가
    def evaluate_piece_for_opponent(self, piece):
        score = 0
        for row, col in self.get_available_locations():
            simulated_board = self.simulate_board(row, col, piece)
            if self.check_win(simulated_board):
                score += WIN_SCORE
            score -= self.evaluate_threat(simulated_board)
        return score

    # 상대방이 사용할 최적의 조각을 선택
    def select_piece(self):
        best_piece = None
        min_score = float('inf')
        for piece in self.available_pieces:
            score = self.evaluate_piece_for_opponent(piece)
            if score < min_score:
                min_score = score
                best_piece = piece
        return best_piece

    # 위치 제어를 평가
    def evaluate_position_control(self, row, col, piece):
        score = 0
        simulated_board = self.simulate_board(row, col, piece)

        # 중앙 위치에 가중치를 부여
        if (row, col) in self.center_positions:
            score += CENTER_WEIGHT

        # 승리 여부 체크
        if self.check_win(simulated_board):
            score += WIN_SCORE

        # 위협에 대한 페널티 적용
        score -= self.evaluate_threat(simulated_board)
        return score

    # 선택한 조각을 보드에 놓기
    def place_piece(self, selected_piece):
        # 첫 번째 수일 경우 중앙 위치를 우선 선택
        if self.is_first_move():
            for row, col in self.center_positions:
                if self.board[row][col] == 0:
                    return row, col

        # 알파베타 가지치기를 적용하여 가장 좋은 수를 선택
        best_positions = []
        max_score = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        for row, col in self.get_available_locations():
            score = self.evaluate_position_control(row, col, selected_piece)

            # 알파베타 가지치기 적용
            if score > max_score:
                max_score = score
                best_positions = [(row, col)]
            elif score == max_score:
                best_positions.append((row, col))

            # 알파베타 가지치기 로직
            alpha = max(alpha, score)
            if beta <= alpha:
                break  # 더 이상 탐색할 필요가 없음

        # 동점일 경우 랜덤 선택
        return random.choice(best_positions)

    # 첫 번째 수인지 확인하는 함수
    def is_first_move(self):
        return np.count_nonzero(self.board) == 0

    # 사용 가능한 위치를 반환하는 함수
    def get_available_locations(self):
        return [(row, col) for row, col in product(range(BOARD_ROWS), range(BOARD_COLS)) if self.board[row][col] == 0]

    # 보드 상태에 선택된 조각을 놓은 후의 보드를 반환
    def simulate_board(self, row, col, piece):
        simulated_board = np.copy(self.board)
        simulated_board[row][col] = self.pieces.index(piece) + 1
        return simulated_board

    # 승리 여부를 체크하는 함수
    def check_win(self, board):
        def check_line(line):
            if 0 in line:
                return False
            characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in line])
            for i in range(4):
                if len(set(characteristics[:, i])) == 1:
                    return True
            return False

        # 행, 열, 대각선 체크
        for col in range(BOARD_COLS):
            if check_line([board[row][col] for row in range(BOARD_ROWS)]):
                return True
        for row in range(BOARD_ROWS):
            if check_line([board[row][col] for col in range(BOARD_COLS)]):
                return True
        if check_line([board[i][i] for i in range(BOARD_ROWS)]) or check_line([board[i][BOARD_ROWS - i - 1] for i in range(BOARD_ROWS)]):
            return True
        return False

    # 위협을 평가하는 함수
    def evaluate_threat(self, board):
        def check_line_threat(line):
            filled_positions = [piece for piece in line if piece != 0]
            if len(filled_positions) == 3:
                characteristics = np.array([self.pieces[piece_idx - 1] for piece_idx in filled_positions])
                for i in range(4):
                    if len(set(characteristics[:, i])) == 1:
                        return THREAT_PENALTY
            return 0

        # 행, 열, 대각선 위협 체크
        for col in range(BOARD_COLS):
            if check_line_threat([board[row][col] for row in range(BOARD_ROWS)]):
                return THREAT_PENALTY
        for row in range(BOARD_ROWS):
            if check_line_threat([board[row][col] for col in range(BOARD_COLS)]):
                return THREAT_PENALTY
        if check_line_threat([board[i][i] for i in range(BOARD_ROWS)]) or check_line_threat([board[i][BOARD_ROWS - i - 1] for i in range(BOARD_ROWS)]):
            return THREAT_PENALTY
        return 0