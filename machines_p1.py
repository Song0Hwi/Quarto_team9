import numpy as np
import random
from itertools import product
import time
import math

class Node:
    """
    MCTS 알고리즘에서 사용되는 트리 노드
    """
    def __init__(self, state, parent=None):
        self.state = state  # 현재 노드의 상태 (보드 상태, 선택된 말, 등)
        self.parent = parent  # 부모 노드
        self.children = []  # 자식 노드 리스트
        self.visits = 0  # 방문 횟수
        self.value = 0  # 가치 합계
    
    def uct_value(self, exploration_weight=1.4):
        """
        UCT (Upper Confidence Bound for Trees) 값 계산
        """
        if self.visits == 0:
            return float('inf')  # 아직 방문하지 않은 노드는 높은 탐색 우선순위를 부여
        exploitation = self.value / self.visits
        exploration = exploration_weight * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration
    
    def is_fully_expanded(self):
        """
        현재 노드가 모든 가능한 자식을 생성했는지 확인
        """
        return len(self.children) == len(self.state.get_possible_actions())
    
    def best_child(self):
        """
        방문 횟수를 기준으로 가장 좋은 자식 노드 반환
        """
        return max(self.children, key=lambda child: child.visits)

def mcts(initial_state, simulation_count=100000, max_depth=12):
    
    root = Node(initial_state)
    
    for _ in range(simulation_count):
        # 1: 선택
        node = root
        depth = 0
        while not node.is_fully_expanded() and depth < max_depth:
            if node.is_fully_expanded():
                node = node.best_child()
            else:
                # 자식 노드 확장
                node = expand(node)
            depth += 1
        
        # 2: 시뮬레이션
        value = simulate(node.state)
        
        # 3: 역전파
        while node is not None:
            node.visits += 1
            node.value += value
            node = node.parent
    
    # 최적의 행동 반환
    return root.best_child().state.action

def expand(node):
    
    untried_actions = [
        action for action in node.state.get_possible_actions()
        if action not in [child.state.action for child in node.children]
    ]
    action = random.choice(untried_actions)
    new_state = node.state.perform_action(action)
    child_node = Node(new_state, parent=node)
    node.children.append(child_node)
    return child_node

def simulate(state):
    
    simulated_state = state.clone()
    while not simulated_state.is_terminal():
        action = random.choice(simulated_state.get_possible_actions())
        simulated_state = simulated_state.perform_action(action)
    return simulated_state.get_reward()

class P1:
    def __init__(self, board, available_pieces):
        self.pieces = [(i, j, k, l) for i in range(2) for j in range(2) for k in range(2) for l in range(2)]  # 16개의 모든 말
        self.board = board  # 현재 보드 상태 (0: 빈칸, 1~16: 배치된 말의 인덱스)
        self.available_pieces = available_pieces  # 현재 사용 가능한 말들 (튜플 형태)

    def select_piece(self):
       
        start_time = time.time()
        
        class SelectPieceState:
            def __init__(self, available_pieces):
                self.available_pieces = available_pieces
            
            def get_possible_actions(self):
                # 선택 가능한 말 리스트 반환
                return self.available_pieces
            
            def perform_action(self, action):
                # 선택한 말 적용한 새 상태 반환
                new_pieces = self.available_pieces[:]
                new_pieces.remove(action)
                return SelectPieceState(new_pieces)
            
            def clone(self):
                # 현재 상태 복제
                return SelectPieceState(self.available_pieces[:])
            
            def is_terminal(self):
                
                return True
            
            def get_reward(self):
                # 랜덤 보상 부여 
                return random.random()
        
        state = SelectPieceState(self.available_pieces)
        selected_piece = mcts(state, simulation_count=10000, max_depth=7)
        
        end_time = time.time()
        print(f"select_piece 시간 소요: {end_time - start_time:.2f}s")
        return selected_piece

    def place_piece(self, selected_piece):
       
        start_time = time.time()
        
        class PlacePieceState:
            def __init__(self, board, available_locs, selected_piece):
                self.board = board
                self.available_locs = available_locs
                self.selected_piece = selected_piece
            
            def get_possible_actions(self):
                # 배치 가능 위치 리스트 반환
                return self.available_locs
            
            def perform_action(self, action):
                # 선택 위치 적용한 새 상태 반환
                new_board = self.board.copy()
                new_board[action[0]][action[1]] = selected_piece
                new_locs = self.available_locs[:]
                new_locs.remove(action)
                return PlacePieceState(new_board, new_locs, self.selected_piece)
            
            def clone(self):
                # 현재 상태 복제
                return PlacePieceState(self.board.copy(), self.available_locs[:], self.selected_piece)
            
            def is_terminal(self):
                
                return True
            
            def get_reward(self):
                # 랜덤 보상 
                return random.random()
        
        available_locs = [(row, col) for row, col in product(range(4), range(4)) if self.board[row][col] == 0]
        state = PlacePieceState(self.board, available_locs, selected_piece)
        best_location = mcts(state, simulation_count=10000, max_depth=7)
        
        end_time = time.time()
        print(f"place_piece 시간 소요: {end_time - start_time:.2f}s")
        return best_location
