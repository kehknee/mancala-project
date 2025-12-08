from math import inf
import copy
import random

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

        # 'Capture Rule' - explained in each comment
        if (pos in self.user_cups(player)  # if cup is on your side,
                and self.cups[pos] == 1):  # cup is empty before last stone was placed
            opposite = 12 - pos  
            captured = self.cups[opposite] # capture stones of opponent's cup opposite of cup you landed on
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
        # The game will end if one player's entire side of cups is fully empty
        side0_empty = all(self.cups[i] == 0 for i in self.user_cups(0))
        side1_empty = all(self.cups[i] == 0 for i in self.user_cups(1))
        return side0_empty or side1_empty

    def sweep_remaining(self):
        """When game is over, remaining stones go into each player's mancala depending on the stones on the sides"""
        # player 0 side
        side0_stones = sum(self.cups[i] for i in self.user_cups(0))
        for i in self.user_cups(0):
            self.cups[i] = 0
        self.cups[self.mancala_index(0)] += side0_stones
        # player 1 side
        side1_stones = sum(self.cups[i] for i in self.user_cups(1))
        for i in self.user_cups(1):
            self.cups[i] = 0
        self.cups[self.mancala_index(1)] += side1_stones

    def score(self):
        return self.cups[6], self.cups[13]

    def winner(self):
        """Return 0 if player 0 wins, 1 if player 1 wins, or None for tie."""
        s0, s1 = self.score()
        if s0 > s1:
            return 0
        elif s1 > s0:
            return 1
        else:
            return None

    def print_space(self):
        user_row = [12, 11, 10, 9, 8, 7]
        agent_row = [0, 1, 2, 3, 4, 5]

        print(" " * 33 + "AI Agent")
        print(" " * 25 + " | ".join(f"{self.cups[i]:2d}" for i in user_row))
        print(f"{self.cups[13]:>14} {' ' * 43} {self.cups[6]:<3}")
        print(" " * 25 + " | ".join(f"{self.cups[i]:2d}" for i in agent_row))
        print(" " * 35 + "User\n")                                                                                             # JC: Swapped for proper user view in terminal

def alphabeta(space: MancalaSpace, 
              depth: int, 
              current_player: int, 
              ai_player: int, 
              alpha: float, 
              beta: float, 
              playstyle_func):
    """ Depth-limited minimax with alpha–beta pruning. Space is current board, playstyle_func: heuristic eval function(space, ai_player) -> float """

    if depth == 0 or space.is_game_over():
        return playstyle_func(space, ai_player)

    open_moves = space.open_moves_moves(current_player)
    
    def move_sort_key(move):
        temp = copy.deepcopy(space)
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
            analyze_space_board = copy.deepcopy(space)
            next_player, extra_turn, game_over = analyze_space_board.apply_move(current_player, move)

            # If you get an extra turn and game not over, don't change player or depth
            if extra_turn and not game_over:
                child_value = alphabeta(analyze_space_board, depth, current_player, ai_player, alpha, beta, playstyle_func)
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
            analyze_space_board = copy.deepcopy(space)
            next_player, extra_turn, game_over = analyze_space_board.apply_move(current_player, move)

            if extra_turn and not game_over:
                child_value = alphabeta(analyze_space_board, depth, current_player, ai_player, alpha, beta, playstyle_func)
            else:
                child_value = alphabeta(analyze_space_board, depth - 1, next_player, ai_player, alpha, beta, playstyle_func)
            value = min(value, child_value)
            beta = min(beta, value)
            if beta <= alpha:  
                break
        return value

def iddfs_best_move(space: MancalaSpace, current_player: int, max_depth: int, playstyle_func=None):
    if playstyle_func is None:
        playstyle_func = base_playstyle

    final_best_move = None

    for depth in range(1, max_depth + 1):
        best_move = None
        best_score = -inf

        for move in space.open_moves_moves(current_player):
            analyze_space_board = copy.deepcopy(space)
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

def base_playstyle(space: MancalaSpace, AI_agent: int):
    AI = space.mancala_index(AI_agent)
    user = space.opponent_mancala_index(AI_agent)

    score_difference = space.cups[AI] - space.cups[user]
    AI_side = sum(space.cups[i] for i in space.user_cups(AI_agent))
    user_side = sum(space.cups[i] for i in space.user_cups(1 - AI_agent))

    return score_difference + 0.1 * (AI_side - user_side)                                                                       # JC: Each return for every playstyle has bias weights added that we can adjust if needed

def agro_playstyle(space: MancalaSpace, AI_agent: int):                                                                          # JC: Capture move mode
    base = base_playstyle(space, AI_agent)
    return base + 5

def extra_turn_playstyle(space: MancalaSpace, AI_agent: int):
    base = base_playstyle(space, AI_agent)
    return base + 3

playstyle_options = [base_playstyle, agro_playstyle, extra_turn_playstyle]

def prompt_user_move(space: MancalaSpace) -> int:
    """Prompt user for legal moves only, reprompting user to try again on any invalid inputs"""
    while True:
        try:
            move = int(input("Choose a put index (0-5): "))
        except ValueError:
            print("Invalid input! Please enter an integer between 0 and 5. Try again...")
            continue

        if move not in space.user_cups(0):
            print("Out of Range! Choose a valid pit index between 0 and 5 on your side!")
            continue

        if space.cups[move] == 0:
            print("That put is empty. Please pick a pit with stones and try again...")
            continue

        return move

if __name__ == "__main__":
    
    space = MancalaSpace.game_start()
    current_player = 0  # 0 = human, 1 = AI

    while True:
        space.print_space()

        if space.is_game_over():
            print("Game over!")
            s0, s1 = space.score()
            print(f"Final score – You (player 0): {s0}, AI (player 1): {s1}")
            winner = space.winner()
            if winner is None:
                print("Tie")
            elif winner == 0:
                print("You win!")
            else:
                print("AI wins.")
            break

        if current_player == 0:
            print("Your turn (player 0).")
            print("Your open_moves moves:", space.open_moves_moves(0))
            move = prompt_user_move(space)
            #move = int(input("Choose a pit index (0–5): "))
        else:
            # AI move
            playstyle_func = random.choice(playstyle_options)
            print(f"AI selected evaluation: {playstyle_func.__name__}")                                                       # JC: Temp print so that we can see while testing

            print("AI is thinking...")
            move = iddfs_best_move(space, current_player=1, max_depth=6, playstyle_func=playstyle_func)
            #move = best_move_determination(space, current_player=1, possible_moves=6, playstyle_func=base_playstyle)
            print(f"AI chooses pit {move}")

        current_player, extra_turn_turn, game_over = space.apply_move(current_player, move)