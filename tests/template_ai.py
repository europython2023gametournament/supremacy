import numpy as np

from supremacy.core.ai import Ai
from supremacy import config

CREATOR = 'JohnDoe'


class PlayerAi(Ai):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, creator=CREATOR, **kwargs)
        # self.previous_position = [0, 0]
        # self.previous_health = 0

    def run(self, t: float, dt: float, info: dict, batch):

        for base in info['bases']:
            if base.mines < 2:
                if base.crystal > config.cost['mine']:
                    base.build_mine()
            elif base.crystal > config.cost['ship']:
                base.build_ship(heading=360 * np.random.random(), batch=batch)
            # elif base.crystal > config.cost['tank']:
            #     base.build_tank(heading=360 * np.random.random(), batch=batch)

            for name, tank in base.tanks.items():
                if hasattr(tank, 'previous_position'):
                    if all(tank.position == tank.previous_position):
                        tank.heading = np.random.random() * 360.0
                tank.previous_position = tank.position

            for name, ship in base.ships.items():
                if hasattr(tank, 'previous_position'):
                    if all(tank.position == tank.previous_position):
                        if ship.get_distance([base.x, base.y]) > 20:
                            ship.convert_to_base()
                        else:
                            ship.heading = np.random.random() * 360.0
                ship.previous_position = ship.position

            # for v in base.vehicles:
            #     if hasattr(v, 'previous_position'):
            #         if all(v.position == v.previous_position):
            #             v.heading = np.random.random() * 360.0
            #     v.previous_position = v.position
