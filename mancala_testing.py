import sys
import time
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
        cups[6] = 0     # Player 0 store
        cups[13] = 0    # Player 1 store
        return MancalaSpace(cups)

    def user_cups(self, player: int):
        return range(0, 6) if player == 0 else range(7, 13)

    def mancala_index(self, player: int):
        return 6 if player == 0 else 13

    def opponent_mancala_index(self, player: int):
        return 13 if player == 0 else 6

    def open_moves_moves(self, player: int):
        return [i for i in self.user_cups(player) if self.cups[i] > 0]
    
    def copy(self):
        return MancalaSpace(self.cups[:])

    def apply_move(self, player: int, cup_index: int):
        if cup_index not in self.user_cups(player):
            raise ValueError("Invalid cup")
        if self.cups[cup_index] == 0:
            raise ValueError("Cup empty")

        stones = self.cups[cup_index]
        self.cups[cup_index] = 0

        own_store = self.mancala_index(player)
        opp_store = self.opponent_mancala_index(player)

        pos = cup_index
        while stones > 0:
            pos = (pos + 1) % 14
            if pos == opp_store:
                continue
            self.cups[pos] += 1
            stones -= 1

        extra_turn = (pos == own_store)

        # Capture rule
        if pos in self.user_cups(player) and self.cups[pos] == 1:
            opposite = 12 - pos
            captured = self.cups[opposite]
            if captured > 0:
                self.cups[opposite] = 0
                self.cups[pos] = 0
                self.cups[own_store] += captured + 1

        game_over = self.is_game_over()
        if game_over:
            self.sweep_remaining()

        next_player = player if (extra_turn and not game_over) else 1 - player
        return next_player, extra_turn, game_over

    def is_game_over(self):
        side0 = all(self.cups[i] == 0 for i in self.user_cups(0))
        side1 = all(self.cups[i] == 0 for i in self.user_cups(1))
        return side0 or side1

    def sweep_remaining(self):
        side0 = sum(self.cups[i] for i in self.user_cups(0))
        for i in self.user_cups(0):
            self.cups[i] = 0
        self.cups[6] += side0

        side1 = sum(self.cups[i] for i in self.user_cups(1))
        for i in self.user_cups(1):
            self.cups[i] = 0
        self.cups[13] += side1

    def score(self):
        return self.cups[6], self.cups[13]

    def winner(self):
        s0, s1 = self.score()
        if s0 > s1: return 0
        if s1 > s0: return 1
        return None

def alphabeta(space, depth, current_player, ai_player, alpha, beta, eval_func):
    global NODE_COUNTER
    NODE_COUNTER += 1

    if depth == 0 or space.is_game_over():
        return eval_func(space, ai_player)

    moves = space.open_moves_moves(current_player)
    if not moves:
        return eval_func(space, ai_player)

    def move_score(m):
        temp = space.copy()
        n, e, g = temp.apply_move(current_player, m)
        return eval_func(temp, ai_player)

    maximizing = (current_player == ai_player)

    if maximizing:
        moves.sort(key=move_score, reverse=True)
        value = -inf
        for move in moves:
            child = space.copy()
            n, e, g = child.apply_move(current_player, move)
            if e and not g:
                score = alphabeta(child, max(1, depth-1), current_player, ai_player, alpha, beta, eval_func)
            else:
                score = alphabeta(child, depth-1, n, ai_player, alpha, beta, eval_func)
            value = max(value, score)
            alpha = max(alpha, value)
            if alpha >= beta: break
        return value

    else:
        moves.sort(key=move_score)
        value = inf
        for move in moves:
            child = space.copy()
            n, e, g = child.apply_move(current_player, move)
            if e and not g:
                score = alphabeta(child, max(1, depth-1), current_player, ai_player, alpha, beta, eval_func)
            else:
                score = alphabeta(child, depth-1, n, ai_player, alpha, beta, eval_func)
            value = min(value, score)
            beta = min(beta, value)
            if alpha >= beta: break
        return value

def iddfs_best_move(space, current_player, max_depth, eval_func):
    global NODE_COUNTER
    NODE_COUNTER = 0

    best_move = None
    best_score = -inf

    for depth in range(1, max_depth + 1):
        for move in space.open_moves_moves(current_player):
            child = space.copy()
            n, e, g = child.apply_move(current_player, move)

            if e and not g:
                score = alphabeta(child, depth, current_player, current_player, -inf, inf, eval_func)
            else:
                score = alphabeta(child, depth-1, n, current_player, -inf, inf, eval_func)

            if score > best_score:
                best_score = score
                best_move = move

    return best_move

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

    # # Old Aggressive Playstyle
    # base = base_playstyle(space, AI_agent)
    # return base + 5

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

    # # Old Extra Turn Playstyle
    # base = base_playstyle(space, AI_agent)
    # return base + 3

playstyle_options = [base_playstyle, aggressive_playstyle, extra_turn_playstyle]              # Used when play testing so either opponent can random.choice(playstyle_options)

# New addition to test run game(s) against another opponet for large numbered simulations
def run_single_game(show_full=True):
    global NODE_COUNTER
    space = MancalaSpace.game_start()
    current_player = 0
    game_over = False

    total_nodes = 0
    ai_moves = 0
    ai_thinking_total = 0.0

    while not game_over:
        if current_player == 0: 
            # These three options were uncommented one at a time upon play testing. If needed, reapply comment for the two not being used to play test for opponent vs AI agent

            # # 1.) AI AGENT LOGIC "USER": tests the logic from our AI agent and determines if it can beat itself
            # eval_func = extra_turn_playstyle                      # Can switch to any playstyle or random.choice()
            # start_time = time.time()
            # move = iddfs_best_move(space, 0, max_depth=4, eval_func=eval_func)
            # end_time = time.time()
            # thinking_time = end_time - start_time

            # if show_full:
            #     print(f"Player 0 (USER) plays pit {move} using {eval_func.__name__} [Time: {thinking_time:.3f}s]")

            # current_player, e, game_over = space.apply_move(0, move)

            # # 2.) RANDOM PIT "USER": choose pit at random
            # move = random.choice(space.open_moves_moves(0)) 
            # if show_full: 
            #     print(f"Random agent (P0) plays pit {move}") 

            # current_player, e, game_over = space.apply_move(0, move)

            # 3.) GREEDY "USER": choose move that maximizes immediate gain
            best_move = None
            best_gain = -1

            for pit in space.open_moves_moves(0):
                temp_space = space.copy()
                next_player, extra_turn, _ = temp_space.apply_move(0, pit)
                
                gain = temp_space.cups[space.mancala_index(0)] - space.cups[space.mancala_index(0)]

                if gain > best_gain:
                    best_gain = gain
                    best_move = pit

            move = best_move
            if show_full:
                print(f"Greedy agent (P0) plays pit {move} (gain {best_gain})")

            current_player, e, game_over = space.apply_move(0, move)
        else:
            # AI AGENT
            eval_func = base_playstyle                     # Can switch to any playstyle or random.choice()
            start_time = time.time()
            move = iddfs_best_move(space, 1, max_depth=4, eval_func=eval_func)
            end_time = time.time()
            thinking_time = end_time - start_time

            ai_thinking_total += thinking_time
            total_nodes += NODE_COUNTER
            ai_moves += 1

            if show_full:
                print(f"AI agent (P1) plays pit {move}   [Nodes: {NODE_COUNTER}, Time: {thinking_time:.3f}s]")

            current_player, e, game_over = space.apply_move(1, move)

    s0, s1 = space.score()
    winner = space.winner()
    avg_nodes = total_nodes / max(ai_moves, 1)
    avg_thinking_time = ai_thinking_total / max(ai_moves, 1)

    if show_full:
        print("\nFINAL BOARD:", space.cups)
        print(f"SCORE — P0(Random): {s0}   P1(AI): {s1}")
        if winner is None:
            print("RESULT: Tie")
        else:
            print(f"RESULT: Player {winner} wins")
        print(f"AI avg nodes: {avg_nodes:.2f}, AI avg thinking time: {avg_thinking_time:.3f}s")

    return winner, avg_nodes, space, avg_thinking_time

# New addition to simulate more than one game to gather statistics for AI agent 
def simulate_many_games(n_games=500):                                                   # Max games can be adjusted
    p0_wins = 0
    p1_wins = 0
    ties = 0
    avg_nodes_list = []
    avg_thinking_times = []

    total_p0_score = 0
    total_p1_score = 0

    print(f"\n===== Running {n_games} Mancala Simulations =====\n")

    for i in range(1, n_games + 1):
        print(f"--- Game {i} ---")
        winner, avg_nodes, final_space, avg_thinking_time = run_single_game(show_full=False)                 # Set to True to see full game play out in terminal
        avg_nodes_list.append(avg_nodes)
        avg_thinking_times.append(avg_thinking_time)

        # Final scores
        p0_score = final_space.cups[6]
        p1_score = final_space.cups[13]
        total_p0_score += p0_score
        total_p1_score += p1_score

        print(f"Final Score -> Player 0: {p0_score} | Player 1: {p1_score}")

        if winner is None:
            print("Result: Tie")
            ties += 1
        elif winner == 0:
            print("Result: Player 0 wins")
            p0_wins += 1
        else:
            print("Result: Player 1 wins")
            p1_wins += 1
        print()

    avg_p0_score = total_p0_score / n_games
    avg_p1_score = total_p1_score / n_games
    avg_ai_thinking_time = sum(avg_thinking_times) / n_games

    print("\n===== FINAL RESULTS =====")
    print(f"Player 0 wins: {p0_wins}")
    print(f"Player 1 wins: {p1_wins}")
    print(f"Ties: {ties}")
    print(f"Average Player 0 score: {avg_p0_score:.2f}")
    print(f"Average Player 1 score: {avg_p1_score:.2f}")
    print(f"AI average nodes per move: {sum(avg_nodes_list)/len(avg_nodes_list):.2f}")
    print(f"AI average thinking time per turn: {sum(avg_thinking_times)/len(avg_thinking_times):.4f}s")
    print(f"AI average thinking time per game: {avg_ai_thinking_time:.4f}s")
    print("=================================\n")

if __name__ == "__main__":
    simulate_many_games(500)                             # Adjust to number of tests you want to simulate, don't exceed max set unless actually changing in simulate_many_games function
