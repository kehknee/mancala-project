import pygame
import sys
import time
import threading
from math import inf
import copy
import random

NODE_COUNTER = 0

class MancalaSpace:
    def __init__(self, cups):
        self.cups = cups
    
    @staticmethod
    def game_start(stones_per_cup: int = 4):
        cups = [stones_per_cup] * 14
        cups[6] = 0  # Initial mancala cup with 0 stones
        cups[13] = 0 # Initial mancala cup with 0 stones 
        return MancalaSpace(cups)

    def user_cups(self, player: int):
        return range(0, 6) if player == 0 else range(7, 13)

    def mancala_index(self, player: int) -> int:    # User
        return 6 if player == 0 else 13

    def opponent_mancala_index(self, player: int) -> int:   # Agent
        return 13 if player == 0 else 6

    def open_moves_moves(self, player: int): # Returns what pits each player is allowed to play
        return [i for i in self.user_cups(player) if self.cups[i] > 0]
    
    def copy(self):
        return MancalaSpace(self.cups[:])

    def apply_move(self, player: int, cup_index: int):
        """ Apply move for player based on rules and cup index. Returns (next_player: int, extra_turn_turn: bool, game_over: bool)"""
        # basic validity
        if cup_index not in self.user_cups(player):
            raise ValueError("Chosen cup is not on player's side.")
        if self.cups[cup_index] == 0:
            raise ValueError("Chosen cup is empty.")

        stones = self.cups[cup_index]
        self.cups[cup_index] = 0

        own_store = self.mancala_index(player)
        opp_store = self.opponent_mancala_index(player)

        pos = cup_index

        while stones > 0:
            pos = (pos + 1) % 14 # moves cup clockwise
            if pos == opp_store:
                continue  # skip opponent's mancala (big cup at the end)
            self.cups[pos] += 1
            stones -= 1

        extra_turn_turn = (pos == own_store) # if landed in your own mancala, get an extra_turn turn

        # 'Capture Rule'
        if (pos in self.user_cups(player) and self.cups[pos] == 1):
            opposite = 12 - pos  
            captured = self.cups[opposite]
            if captured > 0:
                self.cups[opposite] = 0
                self.cups[pos] = 0
                self.cups[own_store] += captured + 1

        # If either side has fully empty cups, game is over
        game_over = self.is_game_over() 
        if game_over:
            self.sweep_remaining()

        next_player = player if extra_turn_turn and not game_over else 1 - player
        return next_player, extra_turn_turn, game_over

    def is_game_over(self) -> bool:
        side0_empty = all(self.cups[i] == 0 for i in self.user_cups(0))
        side1_empty = all(self.cups[i] == 0 for i in self.user_cups(1))
        return side0_empty or side1_empty

    def sweep_remaining(self):
        side0_stones = sum(self.cups[i] for i in self.user_cups(0))
        for i in self.user_cups(0):
            self.cups[i] = 0
        self.cups[self.mancala_index(0)] += side0_stones
        side1_stones = sum(self.cups[i] for i in self.user_cups(1))
        for i in self.user_cups(1):
            self.cups[i] = 0
        self.cups[self.mancala_index(1)] += side1_stones

    def score(self):
        return self.cups[6], self.cups[13]

    def winner(self):
        s0, s1 = self.score()
        if s0 > s1:
            return 0
        elif s1 > s0:
            return 1
        else:
            return None

def alphabeta(space: MancalaSpace, 
              depth: int, 
              current_player: int, 
              ai_player: int, 
              alpha: float, 
              beta: float, 
              playstyle_func):
    
    global NODE_COUNTER
    NODE_COUNTER += 1

    if depth == 0 or space.is_game_over():
        return playstyle_func(space, ai_player)

    open_moves = space.open_moves_moves(current_player)
    
    def move_sort_key(move):
        temp = space.copy()
        next_player, extra_turn, game_over = temp.apply_move(current_player, move)
        return playstyle_func(temp, ai_player)
    
    if current_player == ai_player:
        open_moves.sort(key=move_sort_key, reverse=True)
    else:
        open_moves.sort(key=move_sort_key)        
    
    if not open_moves:
        return playstyle_func(space, ai_player)

    maximizing = (current_player == ai_player)

    if maximizing:
        value = -inf
        for move in open_moves:
            analyze_space_board = space.copy()
            next_player, extra_turn, game_over = analyze_space_board.apply_move(current_player, move)

            if extra_turn and not game_over:
                child_value = alphabeta(analyze_space_board, max(1, depth-1), current_player, ai_player, alpha, beta, playstyle_func)
            else:
                child_value = alphabeta(analyze_space_board, depth - 1, next_player, ai_player, alpha, beta, playstyle_func)

            value = max(value, child_value)
            alpha = max(alpha, value)
            if beta <= alpha:  
                break
        return value

    else:  # minimizing
        value = inf
        for move in open_moves:
            analyze_space_board = space.copy()
            next_player, extra_turn, game_over = analyze_space_board.apply_move(current_player, move)

            if extra_turn and not game_over:
                child_value = alphabeta(analyze_space_board, max(1, depth-1), current_player, ai_player, alpha, beta, playstyle_func)
            else:
                child_value = alphabeta(analyze_space_board, depth - 1, next_player, ai_player, alpha, beta, playstyle_func)
            value = min(value, child_value)
            beta = min(beta, value)
            if beta <= alpha:  
                break
        return value

def iddfs_best_move(space: MancalaSpace, current_player: int, max_depth: int, playstyle_func=None):

    global NODE_COUNTER
    NODE_COUNTER = 0

    if playstyle_func is None:
        playstyle_func = base_playstyle

    final_best_move = None

    for depth in range(1, max_depth + 1):
        best_move = None
        best_score = -inf

        for move in space.open_moves_moves(current_player):
            analyze_space_board = space.copy()
            next_player, extra_turn, game_over = analyze_space_board.apply_move(current_player, move)

            if extra_turn and not game_over:
                score = alphabeta(analyze_space_board, depth, current_player, current_player, alpha=-inf, beta=inf, playstyle_func=playstyle_func)
            else:
                score = alphabeta(analyze_space_board, depth - 1, next_player, current_player, alpha=-inf, beta=inf, playstyle_func=playstyle_func)

            if score > best_score or best_move is None:
                best_score = score
                best_move = move

        final_best_move = best_move

    return final_best_move

def base_playstyle(space, ai):
    AI = space.mancala_index(ai)
    user = space.opponent_mancala_index(ai)
    score_difference = space.cups[AI] - space.cups[user]
    AI_side = sum(space.cups[i] for i in space.user_cups(ai))
    user_side = sum(space.cups[i] for i in space.user_cups(1 - ai))
    return score_difference + 0.1 * (AI_side - user_side)

def aggressive_playstyle(space: MancalaSpace, AI_agent: int):
    base = base_playstyle(space, AI_agent)

    capture_bonus = 0
    for index in space.user_cups(AI_agent):
        stones = space.cups[index]
        if stones == 0:
            continue
        end_pos = (index + stones) % 14
        if end_pos in space.user_cups(AI_agent) and space.cups[end_pos] == 0:
            opposite = 12 - end_pos
            capture_bonus += space.cups[opposite]  

    return base + 5 * capture_bonus  

def extra_turn_playstyle(space: MancalaSpace, AI_agent: int):
    base = base_playstyle(space, AI_agent)

    extra_turn_bonus = 0
    for index in space.user_cups(AI_agent):
        stones = space.cups[index]
        if stones == 0:
            continue
        end_pos = (index + stones) % 14
        if end_pos == space.mancala_index(AI_agent):
            extra_turn_bonus += 1  

    return base + 10 * extra_turn_bonus  

playstyle_options = [base_playstyle, aggressive_playstyle, extra_turn_playstyle]

# New Addition of playable GUI through pygame for user convenience

TOP_ROW = [12,11,10,9,8,7]
BOTTOM_ROW = [0,1,2,3,4,5]
LEFT_MANCALA = 13
RIGHT_MANCALA = 6

# Change Colors If Needed
BG = (30, 30, 30)
BOARD = (210, 180, 140)
TEXT = (10, 10, 10)
HIGHLIGHT = (200, 220, 255)
LEGAL = (120, 200, 120)

pygame.init()
FONT = pygame.font.SysFont("Arial", 18)
BIGFONT = pygame.font.SysFont("Arial", 28)

WIDTH, HEIGHT = 900, 420
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mancala - GUI")

# Layout of Game Display
MARGIN_X = 60
MARGIN_Y = 40
PIT_W = 90
PIT_H = 70
GAP_SPACE = 12
MANCALA_W = 80
MANCALA_H = 240

def compute_pit_positions():
    positions = {}
    y_top = MARGIN_Y                                              # For the top row
    x = MARGIN_X + MANCALA_W + GAP_SPACE
    for index in TOP_ROW:
        positions[index] = pygame.Rect(x, y_top, PIT_W, PIT_H)
        x += PIT_W + GAP_SPACE
    positions[RIGHT_MANCALA] = pygame.Rect(x, MARGIN_Y, MANCALA_W, MANCALA_H)              # Right Mancala Rect is for users store
    x = MARGIN_X
    positions[LEFT_MANCALA] = pygame.Rect(x, MARGIN_Y, MANCALA_W, MANCALA_H)               # Left Mancala Rect is for AI's store
    x = MARGIN_X + MANCALA_W + GAP_SPACE
    y_bottom = MARGIN_Y + MANCALA_H - PIT_H
    x = MARGIN_X + MANCALA_W + GAP_SPACE
    for index in BOTTOM_ROW:
        positions[index] = pygame.Rect(x, y_bottom, PIT_W, PIT_H)
        x += PIT_W + GAP_SPACE
    return positions

PIT_POS = compute_pit_positions()

def draw_board(space: MancalaSpace, current_player, legal_moves=None, message="", prev_ai_move=None, prev_ai_playstyle=None):
    SCREEN.fill(BG)

    # Board basic background
    board_rect = pygame.Rect(MARGIN_X, MARGIN_Y - 6, WIDTH - 2*MARGIN_X, MANCALA_H + 12)
    pygame.draw.rect(SCREEN, BOARD, board_rect, border_radius=12)

    # Draw pits & mancala stores 
    for index, rect in PIT_POS.items():
        color = (255,255,255)
        if index in (LEFT_MANCALA, RIGHT_MANCALA):
            pygame.draw.rect(SCREEN, (230, 210, 170), rect, border_radius=10)
        else:
            pit_bg = (245, 235, 205)
            if legal_moves and index in legal_moves:
                pygame.draw.ellipse(SCREEN, LEGAL, rect.inflate(-6, -6))
            else:
                pygame.draw.ellipse(SCREEN, pit_bg, rect.inflate(-6, -6))

        # Display number value of stones on each pit
        count_text = FONT.render(str(space.cups[index]), True, TEXT)
        SCREEN.blit(count_text, (rect.centerx - count_text.get_width()/2, rect.centery - count_text.get_height()/2))

        index_label = FONT.render(str(index), True, (90,90,90))
        SCREEN.blit(index_label, (rect.x + 4, rect.y + 4))

    # Draw scores
    s0, s1 = space.score()
    score_text = BIGFONT.render(f"You: {s0}    AI: {s1}", True, (250,250,250))
    SCREEN.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 8))

    # Tells user whose turn it is
    turn_text = FONT.render(f"Turn: {'You (0)' if current_player==0 else 'AI (1)'}", True, (230,230,230))
    SCREEN.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, HEIGHT - 68))

    # Shows user what the AI did a move before (pit selection and playstyle selection)
    if prev_ai_move is not None and prev_ai_playstyle is not None:
        prev_text = FONT.render(f"Previous AI Move: pit {prev_ai_move} using {prev_ai_playstyle}", True, (250,250,250))
        SCREEN.blit(prev_text, (WIDTH//2 - prev_text.get_width()//2, HEIGHT - 48))

    # Tells the user if the AI agent is thinking or committing a move 
    if message:
        msg = FONT.render(message, True, (250,250,250))
        SCREEN.blit(msg, (WIDTH - msg.get_width() - 12, HEIGHT - 28))

    # For new player purposes
    instr = FONT.render("Click your pits (0-5) to move. Press R to restart. Esc to quit.", True, (200,200,200))
    SCREEN.blit(instr, (12, HEIGHT - 28))

    pygame.display.flip()


def pit_at_pos(pos):
    for index, rect in PIT_POS.items():
        if rect.collidepoint(pos):
            return index
    return None

# This is the Game state and loop to run pygame
def main():
    clock = pygame.time.Clock()
    space = MancalaSpace.game_start(stones_per_cup=4)
    current_player = 0                                     # 0 user bottom, 1 AI top
    ai_thinking = False
    ai_thread = None
    ai_choice = None
    message = ""
    game_over = False
    prev_ai_move = None
    prev_ai_playstyle = None
    ai_printed_nodes = False


    def ai_move_worker(board_snapshot, selected_playstyle):
        nonlocal ai_choice, ai_thinking, message
        try:
            ai_choice = iddfs_best_move(board_snapshot, current_player=1, max_depth=2, playstyle_func=selected_playstyle)
        except Exception as e:
            ai_choice = None
            print("AI error", e)
        ai_thinking = False

    while True:
        clock.tick(30)

        legal = space.open_moves_moves(0) if not game_over else []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    space = MancalaSpace.game_start(stones_per_cup=4)
                    current_player = 0
                    ai_thinking = False
                    ai_choice = None
                    message = ""
                    game_over = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                if current_player == 0 and not ai_thinking:
                    pos = pygame.mouse.get_pos()
                    pit = pit_at_pos(pos)
                    if pit is not None and pit in space.user_cups(0) and space.cups[pit] > 0:
                        try:
                            current_player, extra_turn, move_game_over = space.apply_move(current_player, pit)
                            if move_game_over:
                                game_over = True
                                s0, s1 = space.score()
                                winner = space.winner()
                                if winner is None:
                                    message = f"Game over. Tie! Final You: {s0} AI: {s1}"
                                elif winner == 0:
                                    message = f"Game over. You win! Final You: {s0} AI: {s1}"
                                else:
                                    message = f"Game over. AI wins. Final You: {s0} AI: {s1}"
                            else:
                                message = ""
                        except Exception as e:
                            message = str(e)

        if not game_over and current_player == 1 and not ai_thinking:
            ai_thinking = True
            ai_choice = None
            selected_playstyle = base_playstyle                        # Can be changed to specific playstyle or random.choice()
            message = "AI thinking..."
            snapshot = space.copy()
            ai_thread = threading.Thread(target=ai_move_worker, args=(snapshot, selected_playstyle))
            ai_thread.start()

        if ai_choice is not None and not game_over:
            if not ai_printed_nodes:
                print("Nodes evaluated:", NODE_COUNTER)
                ai_printed_nodes = True

            time.sleep(0.35)
            try:
                current_player, extra_turn, move_game_over = space.apply_move(1, ai_choice)

                if move_game_over:
                    game_over = True
                    s0, s1 = space.score()
                    winner = space.winner()

                    if winner is None:
                        message = f"Game over. Tie! Final You: {s0} AI: {s1}"
                    elif winner == 0:
                        message = f"Game over. You win! Final You: {s0} AI: {s1}"
                    else:
                        message = f"Game over. AI wins. Final You: {s0} AI: {s1}"
                else:
                    message = f"AI chose pit {ai_choice}"

                prev_ai_move = ai_choice
                prev_ai_playstyle = selected_playstyle.__name__

            except Exception as e:
                message = f"AI error: {e}"

            ai_choice = None
            ai_printed_nodes = False

        # Draw the game through pygame
        legal_moves = space.open_moves_moves(0) if current_player == 0 and not game_over else []
        draw_board(space, current_player, legal_moves, message=message,
           prev_ai_move=prev_ai_move, prev_ai_playstyle=prev_ai_playstyle)

if __name__ == "__main__":
    main()
