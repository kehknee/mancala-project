# mancala-project
Mancala game playing agent using AI algorithms
All AI algorithms + game space and rules are included within mancala.py

How to play:
1. Install Python
2. Run file in IDE or any code runner with a terminal
3. Check terminal, play by inputting numbers based on moves available for user.

🟫 Mancala Rules 
Board Structure

The board has 14 cups:
6 pits per player
Player 0 pits: 0–5
Player 1 pits: 7–12
2 Mancalas (stores)
Player 0’s Mancala: cup 6
Player 1’s Mancala: cup 13
Each non-Mancala pit starts with 4 stones by default.

🎮 Turn Rules
1. Pick a pit
A player selects one of their own pits that contains at least one stone.
2. Sowing
All stones from the selected pit are lifted and distributed counter-clockwise, one per cup.
You skip your opponent’s Mancala, but you may place stones into your own Mancala.

⭐ Special Rules

3. Extra Turn
If your last stone lands in your own Mancala, you take another turn.
4. Capture
A capture occurs when:
Your last stone lands in an empty pit on your side, and
The opposite pit on the opponent’s side contains stones.
When this happens:
You capture all stones from the opposite pit + your last stone,
And place them into your own Mancala.

🛑 End of Game

The game ends when:
One player's 6 pits are all empty.
When that happens:
The other player sweeps all remaining stones on their side into their Mancala.
Final scores are the total stones in each Mancala.

🏆 Winner

The player with more stones in their Mancala wins.
A tie is possible.


Additional Files

🖥️ mancala_GUI

This file provides a graphical version of the Mancala game.

To run mancala_GUI:

1. Make sure you have pygame installed:

        pip install pygame

2. Once installed, run mancala_GUI.py from your IDE, terminal, or code runner.

3. A game window will pop up, allowing you to play Mancala through a graphical interface.


🔬 mancala_testing

This file is used for running automated simulations to test and compare different heuristic functions.

To use mancala_testing:

1. Open the file and select which heuristic functions you want to evaluate.

2. Set the number of simulations you want to run by modifying the following line:

        simulate_many_games(500)

3. Run the file, and the simulations will execute automatically, outputting performance results for the selected heuristics.
