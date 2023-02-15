# SPDX-License-Identifier: BSD-3-Clause


class Ai:

    def __init__(self, creator: str, team: int = None):
        self.team = team
        self.creator = creator

    def run(self, *args, **kwargs):
        return

    def exec(self, t: float, dt: float, info: dict, game_map):
        self.run(t=t, dt=dt, info=info, game_map=game_map)
