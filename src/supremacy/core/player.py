from matplotlib import colors

from .base import Base


class Player:

    def __init__(self, ai, location, number: int):
        self.ai = ai
        self.ai.team = number
        self.name = ai.creator
        self.hq = location
        self.number = number
        self.color = colors.to_hex(f'C{self.number}')
        self.bases = [Base(x=location[0], y=location[1], team=number, color=self.color)]
        # self.tanks = {}
        # self.ships = {}
        # self.jets = {}
        # self.mines = {}

    def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
        if safe:
            try:
                self.ai.exec(t, dt, info)
            except:
                pass
        else:
            self.ai.exec(t, dt, info)
        # if not safe:
        #     nprops = 0
        #     if self.ai.heading is not None:
        #         nprops += 1
        #     if self.ai.goto is not None:
        #         nprops += 1
        #     if self.ai.left is not None:
        #         nprops += 1
        #     if self.ai.right is not None:
        #         nprops += 1
        #     if nprops > 1:
        #         print('Warning, more than one AI property is set, '
        #               'results may be unpredictable!')
        # # try:
        # if self.ai.heading is not None:
        #     self.heading = self.ai.heading
        # if self.ai.goto is not None:
        #     self.goto(*self.ai.goto)
        # if self.ai.left is not None:
        #     self.left(self.ai.left)
        # if self.ai.right is not None:
        #     self.right(self.ai.right)
        # # except:
        # #     print('Error in ', self.ai.creator, self.name)
        # #     pass
