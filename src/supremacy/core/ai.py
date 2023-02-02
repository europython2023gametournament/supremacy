# SPDX-License-Identifier: BSD-3-Clause

import numpy as np


class Ai:

    def __init__(self, creator: str, team: int = None):
        self.team = team
        # self.opposing_team = 'red' if self.team == 'blue' else 'blue'
        # self.kind = kind.lower()
        # self.heading = None
        # self.goto = None
        # self.message = None
        self.creator = creator
        # self.stop = False
        # self.left = None
        # self.right = None

    def run(self, *args, **kwargs):
        return

    def exec(self, t: float, dt: float, info: dict, batch):
        # self.heading = None
        # self.goto = None
        # self.left = None
        # self.right = None
        # self._params = info['me']
        # for base in info['bases']:
        #     base.init_dt()
        self.run(t=t, dt=dt, info=info, batch=batch)
