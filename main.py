import MCTS
import OLDtictactoe
import tictactoe


def main():
    # isPlayer1: bool = True
    # initial_state: tictactoe.TTT_State = tictactoe.TTT_State(
    #     isPlayer1, tictactoe.TTT_Board()
    # )
    initial_state: tictactoe.TTT_state = tictactoe.TTT_state(
        tictactoe.TTT_board(), tictactoe.Players.PLAYER1
    )

    print(MCTS.MonteCarloTreeSearch(initial_state, 2000, True))


if __name__ == "__main__":
    main()
