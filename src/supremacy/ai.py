# SPDX-License-Identifier: BSD-3-Clause

from .tools import eucledian_distance, distance_on_torus


class Ai:

    def run(self, *args, **kwargs):
        return

    # def exec(self, t: float, dt: float, info: dict, game_map):
    #     self.run(t=t, dt=dt, info=info, game_map=game_map.array.filled(-1))  # TODO
    #     # self.run(t=t, dt=dt, info=info, game_map=game_map.array)

    def get_distance(self,
                     xa: float,
                     ya: float,
                     xb: float,
                     yb: float,
                     shortest=True) -> float:
        if not shortest:
            return eucledian_distance(xa, ya, xb, yb)
        else:
            return distance_on_torus(xa, ya, xb, yb)
