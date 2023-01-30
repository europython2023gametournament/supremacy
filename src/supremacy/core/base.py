import uuid

from .vehicles import Tank


class Base:

    def __init__(self, x, y, team, color):
        self.x = x
        self.y = y
        self.team = team
        self.color = color
        self.tanks = {}
        self.ships = {}
        self.jets = {}
        self.mines = 1
        self.crystal = 0

    @property
    def vehicles(self):
        return list(self.tanks.values()) + list(self.ships.values()) + list(
            self.jets.values())

    def build_mine(self):
        self.mines += 1

    def build_tank(self, heading):
        vid = uuid.uuid4()
        self.tanks[vid] = Tank(x=self.x + 5,
                               y=self.y + 5,
                               color=self.color,
                               team=self.team,
                               heading=heading)
        self.crystal -= self.tanks[vid].cost
