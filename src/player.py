from abc import ABC, abstractmethod
import time


class Player(ABC):
    @abstractmethod
    def get_move(self, board):
        pass
