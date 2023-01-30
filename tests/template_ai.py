import numpy as np

from supremacy.core.ai import Ai

CREATOR = 'JohnDoe'


class PlayerAi(Ai):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, creator=CREATOR, **kwargs)
        # self.previous_position = [0, 0]
        # self.previous_health = 0

    def run(self, t: float, dt: float, info: dict):

        for base in info['bases']:
            if base.mines < 3:
                if base.crystal > 500:
                    base.build_mine()
            elif base.crystal > 200:
                base.build_tank(heading=360 * np.random.random())

            # for name, tank in base.tanks.items():
            #     if hasattr(tank, 'previous_position'):
            #         if all(tank.position == tank.previous_position):
            #             tank.heading = np.random.random() * 360.0
            #     tank.previous_position = tank.position
