import MCTS
from enum import Enum
import random


class Players(Enum):
    """
    Enum for representing player options

    Args:
        Enum (class): enumerated type
    """

    PLAYER1 = (1,)
    PLAYER2 = 2


class GameState(Enum):
    """
    Enum for representing the state of the current game
    CONTINUE means the game is in progress
    PLAYER1 means player 1 won
    PLAYER2 means player 2 won
    DRAW means neither player won

    Args:
        Enum (class): enumerated typee
    """

    CONTINUE = (0,)
    PLAYER1 = (1,)
    PLAYER2 = (2,)
    DRAW = 3


class TTT_state(MCTS.AbstractState):
    def __init__(self, board: "TTT_board", player: Players) -> None:
        """
        Initialization of the Tic Tac Toe state

        Args:
            board (TTT_board): game board the state is currently in
            player (Players): the current player of the game state
        """

        self.board: TTT_board = board
        self.player: Players = player

    def terminated(self) -> bool:
        """
        Checks if the state is in a terminating state

        Returns:
            bool: True if the state is in a terminating state
        """
        return self.board.check_game_state() != GameState.CONTINUE

    def random_action(self, actions_taken: list[int] = []) -> tuple[int, "TTT_state"]:
        """
        Performs a random action using the current state
        The next state will the other player, who is the one making the action

        Args:
            actions_taken (list[int]): List of the number representations of previous actions taken
                                        Default to no actions taken previously

        Returns:
            int: number representation of the action taken
            AbstractState: returns the resulting state from the random aciton and current state
        """
        # Filter possible action locations by the actions already taken
        possible_action_locations: list[int] = self.board.possible_actions()
        possible_action_locations = [
            x for x in possible_action_locations if x not in actions_taken
        ]

        # Create a new board using the random action and other player
        random_action: int = random.choice(possible_action_locations)
        other_player: Players = (
            Players.PLAYER2 if self.player == Players.PLAYER1 else Players.PLAYER1
        )
        new_board: TTT_board = self.board.take_action(
            random_action,
            other_player,
        )

        # Return the action number and new state
        return random_action, TTT_state(new_board, other_player)

    def update_value(self, terminationState: "TTT_state") -> int:
        """
        Meant to update the value of a Node based on its current state and the state
        of the node which terminated
        0 if a draw happens
        1 if the current state won
        -1 if the current state lost

        Args:
            terminationState (AbstractState): the state of the node which terminated (most likely a child or child of a child of the current node)

        Returns:
            int: a number which should be added to the current value of the node: node += update_value(...)
        """
        finished_game_state = terminationState.board.check_game_state()

        if finished_game_state == GameState.DRAW:
            return 0

        if finished_game_state == GameState.PLAYER1:
            return 1 if self.player == Players.PLAYER1 else -1

        # Falls through to the finished game state of PLAYER2
        return 1 if self.player == Players.PLAYER2 else -1

    def state_exhausted(self, actions_taken: int) -> bool:
        """
        When given the number of children actions explored, tells the user if the current
        state has exhausted all possibilities

        Args:
            actions_taken (int): number of next actions explored

        Returns:
            bool: true if all future actions have been explored
        """
        return actions_taken >= len(self.board.possible_actions())

    def __str__(self) -> str:
        """
        String representation of the state

        Returns:
            str: string representation of the state
        """
        return self.board.__str__()


class TTT_board:
    def __init__(self, board: list[int] | None = None) -> None:
        self.board: list[int] = [0] * 9 if board is None else board.copy()

    def take_action(self, location: int, player: Players) -> "TTT_board":
        """
        Takes an action on a new board

        Args:
            location (int): index of the board
            player (Players): player taking the action

        Returns:
            TTT_board: a new board with the action taken
        """
        new_board: TTT_board = TTT_board(self.board)
        new_board.board[location] = 1 if player == Players.PLAYER1 else 2
        return new_board

    def possible_actions(self) -> list[int]:
        """
        Filters the board for the indexes that hold a value which is 0

        Returns:
            list[int]: list of board indexes where a move can be made
        """
        return [i for i, v in enumerate(self.board) if v == 0]

    def check_game_state(self) -> GameState:
        """
        Checks the state of the current game board

        Returns:
            GameState: all possible states of the game
        """
        for i in range(3):
            # Check Sideways
            if (
                self.board[3 * i] != 0
                and self.board[3 * i] == self.board[3 * i + 1] == self.board[3 * i + 2]
            ):
                return (
                    GameState.PLAYER1 if self.board[3 * i] == 1 else GameState.PLAYER2
                )
            # Check Vertical
            if (
                self.board[i] != 0
                and self.board[i] == self.board[i + 3] == self.board[i + 6]
            ):
                return GameState.PLAYER1 if self.board[i] == 1 else GameState.PLAYER2

        # Check Diagonal
        if self.board[0] != 0 and self.board[0] == self.board[4] == self.board[8]:
            return GameState.PLAYER1 if self.board[0] == 1 else GameState.PLAYER2
        if self.board[2] != 0 and self.board[2] == self.board[4] == self.board[6]:
            return GameState.PLAYER1 if self.board[2] == 1 else GameState.PLAYER2

        # Check Draw
        if len(self.possible_actions()) == 0:
            return GameState.DRAW

        return GameState.CONTINUE

    def __str__(self) -> str:
        """
        # # #
        # # #
        # # #
        Shows the board in that representation

        Returns:
            str: string representation of the board
        """
        return f"{self.board[0]} {self.board[1]} {self.board[2]} \n{self.board[3]} {self.board[4]} {self.board[5]} \n{self.board[6]} {self.board[7]} {self.board[8]}"


if __name__ == "__main__":
    # Play Tic Tac Toe
    game_board: TTT_board = TTT_board()
    while game_board.check_game_state() == GameState.CONTINUE:
        print(f"{game_board}")
        next_move: int = int(
            input("Type the index of the suqare you want to fill (1-9): ")
        )
        game_board = game_board.take_action(next_move - 1, Players.PLAYER1)
        if game_board.check_game_state() != GameState.CONTINUE:
            break
        game_state = TTT_state(game_board, Players.PLAYER1)
        AI_move: TTT_state = MCTS.MonteCarloTreeSearch(game_state, 1000, DEBUG=True)
        game_board = AI_move.board

    if game_board.check_game_state() is GameState.DRAW:
        print(f"DRAW!\n{game_board}")
    if game_board.check_game_state() is GameState.PLAYER1:
        print(f"WIN!\n{game_board}")
    if game_board.check_game_state() is GameState.PLAYER2:
        print(f"LOSS!\n{game_board}")
