import random


class MatchboxComputer:
    """
    A tic-tac-toe playing computer based on Donald Michie's MENACE.
    """

    def __init__(self):
        """
        Initializes the matchbox computer with empty matchboxes for each possible game state.
        """
        self.matchboxes = {}

    def get_board_state(self, board):
        """
        Converts the tic-tac-toe board into a string representation.
        """
        return "".join(cell for row in board for cell in row)

    def initialize_matchbox(self, board_state):
        """
        Initializes a matchbox for a given board state with beads for each possible move.
        """
        possible_moves = [i for i, cell in enumerate(board_state) if cell == " "]
        self.matchboxes[board_state] = {
            move: ["R", "G", "B"] * 3 for move in possible_moves
        }

    def get_move(self, board):
        """
        Selects a move for the computer based on the current board state.
        """
        board_state = self.get_board_state(board)
        if board_state not in self.matchboxes:
            self.initialize_matchbox(board_state)
        matchbox = self.matchboxes[board_state]
        possible_moves = list(matchbox.keys())
        beads = [bead for move in possible_moves for bead in matchbox[move]]
        chosen_bead = random.choice(beads)
        chosen_move = [
            move for move in possible_moves if chosen_bead in matchbox[move]
        ][0]
        return chosen_move, chosen_bead

    def learn(self, board_history, result, beads_drawn):
        """
        Updates the matchboxes based on the outcome of the game.
        """
        for i, board in enumerate(board_history):
            board_state = self.get_board_state(board)
            move, bead = beads_drawn[i]
            try:
                if result == "win":
                    self.matchboxes[board_state][move].extend([bead, bead])
                elif result == "loss":
                    self.matchboxes[board_state][move].remove(bead)
                elif result == "draw":
                    self.matchboxes[board_state][move].append(bead)
            except Exception as e:
                print(e)
                print("i: ", i)
                print("board: ", board)
                print("Move: ", move)
                print("Bead: ", bead)
                print("board_state: ", f"%s" % board_state)
                print("matchboxes: ", self.matchboxes)
                print("matchboxes Keys: ", self.matchboxes.keys())


def print_board(board):
    """
    Prints the tic-tac-toe board to the console.
    """
    for row in board:
        print("|".join(row))
        print("-" * 5)


def play_game(computer: MatchboxComputer):
    """
    Plays a game of tic-tac-toe between the computer and a human player.
    """
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"
    board_history = []
    beads_drawn = []

    while True:
        print_board(board)
        board_history.append([row[:] for row in board])  # Deep copy of board

        if current_player == "X":
            move, bead = computer.get_move(board)
            print(f"Computer chooses position {move + 1} (bead: {bead})")
            beads_drawn.append((move, bead))
        else:
            while True:
                try:
                    move = int(input("Enter your move (1-9): ")) - 1
                    if 0 <= move <= 8 and board[move // 3][move % 3] == " ":
                        break
                    else:
                        print("Invalid move. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        board[move // 3][move % 3] = current_player

        if check_win(board, current_player):
            print_board(board)
            print(f"{current_player} wins!")
            result = "win" if current_player == "X" else "loss"
            break
        elif check_draw(board):
            print_board(board)
            print("It's a draw!")
            result = "draw"
            break

        current_player = "O" if current_player == "X" else "X"

    computer.learn(board_history, result, beads_drawn)


def check_win(board, player):
    """
    Checks if the given player has won the game.
    """
    # Check rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Check columns
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    # Check diagonals
    if all(board[i][i] == player for i in range(3)) or all(
        board[i][2 - i] == player for i in range(3)
    ):
        return True
    return False


def check_draw(board):
    """
    Checks if the game is a draw.
    """
    return all(cell != " " for row in board for cell in row)


# Main game loop
if __name__ == "__main__":
    computer = MatchboxComputer()
    while True:
        play_game(computer)
        play_again = input("Do you want to play again? (y/n): ")
        if play_again.lower() != "y":
            break
    print("Thanks for playing!")
