from abc import ABC, abstractmethod


class BaseConsole(ABC):
    """
    Where the game reads from and writes to.

    An abstraction rather than print and input, so a test can drive the game loop
    with no terminal attached.
    """

    @abstractmethod
    def write_line(self, text: str) -> None: ...

    @abstractmethod
    def read_line(self, prompt: str) -> str:
        """
        Read one line. Raises EOFError when there is no more input.
        """
