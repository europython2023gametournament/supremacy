from .game_map import GameMap
from .graphics import Graphics


class Engine:

    def __init__(self, players: list, speedup: int = 1):

        self.ng = 4
        self.nx = self.ng * 475
        self.ny = self.ng * 250
        self.game_map = GameMap(nx=self.nx, ny=self.ny, ng=self.ng)
        self.graphics = Graphics(game_map=self.game_map)
