from enum import Enum
import random
from MCTS import AbstractState as State
import MCTS


class Termination(Enum):
    CONTINUE = 0
    PLAYER1 = 1
    PLAYER2 = 2
    DRAW = 3


class TTT_State(State):
    def __init__(self, player1: bool, board: "TTT_Board"):
        self.player1: bool = player1
        self.board: TTT_Board = board
        self.terminate: Termination = Termination.CONTINUE
        self.num_next_states: int = len(board.possible_actions())

    def random_action(self, actions_taken: list[int] = []) -> tuple[int, "TTT_State"]:
        """
        DOES NOT WORK USE NEW VERSION

        Performs a random action using the current state
        The next state will the other player, who is the one making the action

        Args:
            actions_taken (list[int]): List of the number representations of previous actions taken
                                        Default to no actions taken previously

        Returns:
            int: number representation of the action taken
            AbstractState: returns the resulting state from the random aciton and current state
        """
        print("IF YOU SEE THIS THEN IT MEANS YOU ARE USING THE WRONG VERSION")

        # copy current board
        new_board = TTT_Board(self.board.board.copy())

        # Take a random action
        action_locations: list[int] = new_board.possible_actions()
        new_board.action(
            action_locations[random.randint(0, len(action_locations) - 1)],
            2 if self.player1 else 1,
        )

        # create new state as the other player
        new_state = TTT_State(not self.player1, new_board)

        new_state.terminate = new_board.checkGameOver()

        return 0, new_state

    def update_value(self, terminationState: "TTT_State") -> int:
        # if player 1 won and you're player 1 or vice versa, 0 if draw
        if terminationState.terminate == Termination.PLAYER1:
            return 1 if self.player1 else -1
        if terminationState.terminate == Termination.PLAYER2:
            return 1 if not self.player1 else -1
        return 0

    def terminated(self) -> bool:
        return self.terminate is not Termination.CONTINUE

    def state_exhausted(self, actions_taken: int) -> bool:
        return actions_taken >= self.num_next_states

    def __str__(self) -> str:
        return self.board.__str__()


class TTT_Board:
    # 0 means no player
    # 1 means player one
    # 2 means player two

    def __init__(self, board: None | list[int] = None):
        self.board: list[int] = [0] * 9 if board is None else board.copy()
        assert len(self.board) == 9, f"Board is corrupted! Length: {len(self.board)}"

    def action(self, location: int, player: int) -> None:
        self.board[location] = player

    def possible_actions(self) -> list[int]:
        return [k for k, v in enumerate(self.board) if v == 0]

    def checkGameOver(self) -> Termination:
        for i in range(3):
            # Check Sideways
            if (
                self.board[3 * i] != 0
                and self.board[3 * i] == self.board[3 * i + 1] == self.board[3 * i + 2]
            ):
                return (
                    Termination.PLAYER1
                    if self.board[3 * i] == 1
                    else Termination.PLAYER2
                )
            # Check Vertical
            if (
                self.board[i] != 0
                and self.board[i] == self.board[i + 3] == self.board[i + 6]
            ):
                return (
                    Termination.PLAYER1 if self.board[i] == 1 else Termination.PLAYER2
                )

        # Check Diagonal
        if self.board[0] != 0 and self.board[0] == self.board[4] == self.board[8]:
            return Termination.PLAYER1 if self.board[0] == 1 else Termination.PLAYER2
        if self.board[2] != 0 and self.board[2] == self.board[4] == self.board[6]:
            return Termination.PLAYER1 if self.board[2] == 1 else Termination.PLAYER2

        # Check Draw
        if len(self.possible_actions()) == 0:
            return Termination.DRAW

        return Termination.CONTINUE

    def __str__(self) -> str:
        return f"{self.board[0]} {self.board[1]} {self.board[2]} \n{self.board[3]} {self.board[4]} {self.board[5]} \n{self.board[6]} {self.board[7]} {self.board[8]}\n"


if __name__ == "__main__":
    # Play Tic Tac Toe
    game_board: TTT_Board = TTT_Board()
    while game_board.checkGameOver() is Termination.CONTINUE:
        print(f"{game_board}")
        next_move: int = int(
            input("Type the index of the suqare you want to fill (0-8): ")
        )
        game_board.action(next_move, 1)
        if game_board.checkGameOver() != Termination.CONTINUE:
            break
        game_state = TTT_State(True, game_board)
        AI_move: TTT_State = MCTS.MonteCarloTreeSearch(game_state, 1000, DEBUG=True)
        game_board = AI_move.board

    if game_board.checkGameOver() is Termination.DRAW:
        print(f"DRAW!\n{game_board}")
    if game_board.checkGameOver() is Termination.PLAYER1:
        print(f"WIN!\n{game_board}")
    if game_board.checkGameOver() is Termination.PLAYER2:
        print(f"LOSS!\n{game_board}")
