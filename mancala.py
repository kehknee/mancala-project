from math import inf

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

    def legal_moves(self, player: int): # Returns what pits each player is allowed to play
        return [i for i in self.user_cups(player) if self.cups[i] > 0]
    
    def apply_move(self, player: int, cup_index: int):
        """ Apply move for player based on rules and cup index. Returns (next_player: int, extra_turn: bool, game_over: bool)"""
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

        extra_turn = (pos == own_store) # if landed in your own mancala, get an extra turn

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

        next_player = player if extra_turn and not game_over else 1 - player
        return next_player, extra_turn, game_over

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

        print(" " * 35 + "User")
        print(" " * 25 + " | ".join(f"{self.cups[i]:2d}" for i in user_row))
        print(f"{self.cups[13]:>14} {' ' * 43} {self.cups[6]:<3}")
        print(" " * 25 + " | ".join(f"{self.cups[i]:2d}" for i in agent_row))
        print(" " * 33 + "AI Agent\n")

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
            print("Your legal moves:", space.legal_moves(0))
            move = int(input("Choose a pit index (0–5): "))
        else:
            # AI move
            print("AI is thinking...")
            # move = choose_best_move(space, current_player=1, depth=6, eval_fn=simple_eval)
            # TO DO
            # choose_best_move (AI uses to find next best move)
            # eval_fn & simple_eval (evaluation functions for AI to use to decide)
            print(f"AI chooses pit {move}")

        current_player, extra_turn, game_over = space.apply_move(current_player, move)