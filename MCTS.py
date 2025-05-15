import math
from abc import ABC, abstractmethod
from typing import Optional
from typing import TypeVar, Generic


class AbstractState(ABC):
    """
    Abstract Class representing the state of a node

    Args:
        ABC (class): abstract base class
    """

    @abstractmethod
    def terminated(self) -> bool:
        """
        Checks if the state is in a terminating state

        Returns:
            bool: True if the state is in a terminating state
        """
        pass

    @abstractmethod
    def random_action(self, actions_taken: list[int] = []) -> tuple[int, "T"]:
        """
        Performs a random action using the current state

        Args:
            actions_taken (list[int]): List of the number representations of previous actions taken
                                        Default to no actions taken previously

        Returns:
            int: number representation of the action taken
            AbstractState: returns the resulting state from the random aciton and current state
        """
        pass

    @abstractmethod
    def update_value(self, terminationState: "T") -> int:
        """
        Meant to update the value of a Node based on its current state and the state
        of the node which terminated

        Args:
            terminationState (AbstractState): the state of the node which terminate (most likely a child or child of a child of the current node)

        Returns:
            int: a number which should be added to the current value of the node: node += update_value(...)
        """
        pass

    @abstractmethod
    def state_exhausted(self, actions_taken: int) -> bool:
        """
        When given the number of children actions explored, tells the user if the current
        state has exhausted all possibilities

        Args:
            actions_taken (int): number of next actions explored

        Returns:
            bool: true if all future actions have been explored
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        String representation of the state

        Returns:
            str: string representation of the state
        """
        pass


T = TypeVar("T", bound=AbstractState)


class Node(Generic[T]):
    def __init__(self, state: T, parent: Optional["Node[T]"] = None):
        # Normal functionality
        self.children: list[Node[T]] = []
        self.actions_taken: list[int] = []
        self.parent: Node[T] | None = parent

        # Required for MCTS
        self.state: T = state
        self.visits: int = 0
        self.value: int = 0
        self.ucb: float = 0


def calc_UCB(
    child: Node, parent: Node, exploration_param: float = math.sqrt(2)
) -> float:
    """
    UCB formula adapted from
    https://github.com/vgarciasc/mcts-viz/blob/master/lib/mcts.js
    https://medium.com/swlh/tic-tac-toe-at-the-monte-carlo-a5e0394c7bc2

    Args:
        child (Node): next state in calculations
        parent (Node): current state in calculations

    Returns:
        float: a UCB value
    """
    exploitation = child.value / child.visits
    exploration = exploration_param * math.sqrt(math.log(parent.visits) / child.visits)
    return exploitation + exploration


def MonteCarloTreeSearch(initial_state: T, iterations: int, DEBUG: bool = False) -> T:
    """
    Performs the Monte Carlo Tree Search on a Node which represents the current state
    Repeats 4 steps "iterations" # of times:
    1) Selection
    2) Expansion
    3) Simulation
    4) Backpropogation

    Args:
        initial_state (T): initial state/root of the search
        iterations (int): number of iterations taken
        DEBUG (bool): if true, shows debug information

    Returns:
        T: The most optimal next state
    """

    root_node: Node[T] = Node(initial_state)

    for i in range(iterations):
        selected_node: Node[T] = select(root_node)
        expanded_node: Node[T] = expand(selected_node)
        simulated_state: T = simulate(expanded_node)
        backpropogate(expanded_node, simulated_state)

        if i < 10 and DEBUG:
            print(f"{i}th State:")
            print(
                f"Root: {root_node.visits} visits, {root_node.value} value, {root_node.ucb} ucb"
            )
            for i, child in enumerate(root_node.children):
                print(
                    f"Child {i}: {child.visits} visits, {child.value} value, {child.ucb} ucb"  # \n{child.state}
                )

    # Chose child with the most visits
    most_visited: Node[T] = sorted(
        root_node.children, key=lambda n: n.visits, reverse=True
    )[0]

    # Debug Info
    if DEBUG:
        print("Final State:")
        print(
            f"Root: {root_node.visits} visits, {root_node.value} value, {root_node.ucb} ucb"
        )
        for i, child in enumerate(root_node.children):
            print(
                f"Child {i}: {child.visits} visits, {child.value} value, {child.ucb} ucb"  # \n{child.state}
            )
        print(
            f"Best Choice: {most_visited.visits} visits, {most_visited.value} value, {most_visited.ucb} ucb\n{most_visited.state}"
        )
        for i, child in enumerate(most_visited.children):
            print(
                f"Best Children {i}: {child.visits} visits, {child.value} value, {child.ucb} ucb"  # \n{child.state}
            )

    return most_visited.state


def select(root: Node[T]) -> Node[T]:
    temp_node: Node[T] = root
    while len(temp_node.children) > 0 and temp_node.state.state_exhausted(
        len(temp_node.children)
    ):
        # Set the next temp_node to the child with the highest UCB
        max_ucb_child: Node[T] = temp_node.children[0]
        for child in temp_node.children:
            child.ucb = calc_UCB(child, temp_node)
            if child.ucb > max_ucb_child.ucb:
                max_ucb_child = child
        temp_node = max_ucb_child

    return temp_node


def expand(current_node: Node[T]) -> Node[T]:
    # Cannot expand terminated nodes
    if current_node.state.terminated():
        return current_node

    # Explicit typing
    action_number: int
    next_state: T
    action_number, next_state = current_node.state.random_action(
        actions_taken=current_node.actions_taken
    )
    # Add action to taken list
    current_node.actions_taken.append(action_number)

    # Ensure proper generations
    next_node: Node[T] = Node(next_state, current_node)
    current_node.children.append(next_node)

    return next_node


def simulate(current_node: Node[T]) -> T:
    sim_state: T = current_node.state

    while not sim_state.terminated():
        _, sim_state = sim_state.random_action()

    return sim_state


def backpropogate(current_node: Node[T], sim_state: T) -> None:
    # Update visits and value of the current node and its parents
    while current_node.parent is not None:
        current_node.value += current_node.state.update_value(sim_state)
        current_node.visits += 1
        current_node = current_node.parent

    # Update visits of root node
    current_node.visits += 1
