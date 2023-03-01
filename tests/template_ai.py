import numpy as np

CREATOR = 'JohnDoe'


class PlayerAi(Ai):

    def __init__(self):
        super().__init__()
        self.team = CREATOR

        self.previous_positions = {}
        self.ntanks = {}
        self.nships = {}

    def run(self, t: float, dt: float, info: dict, game_map):

        myinfo = info[self.team]
        for base in myinfo['bases']:
            # print(base._data)
            if base.uid not in self.ntanks:
                self.ntanks[base.uid] = 0
            if base.uid not in self.nships:
                self.nships[base.uid] = 0
            if base.mines < 3:
                if base.crystal > base.cost('mine'):
                    base.build_mine()
            elif base.crystal > base.cost('tank') and self.ntanks[base.uid] < 5:
                base.build_tank(heading=360 * np.random.random())
                self.ntanks[base.uid] += 1
            elif base.crystal > base.cost('ship') and self.nships[base.uid] < 3:
                base.build_ship(heading=360 * np.random.random())
                self.nships[base.uid] += 1
            elif base.crystal > base.cost('jet'):
                base.build_jet(heading=360 * np.random.random())
                # self.ntanks[base['uid']] = 0
                # self.nships[base['uid']] += 1
            # elif base['crystal'] > config.cost['ship']:
            #     base.build_ship(heading=360 * np.random.random())
            #     self.ntanks[base['uid']] = 0
            #     self.nships[base['uid']] += 1

        target = None
        if len(info) > 1:
            for name in info:
                if name != self.team:
                    if 'bases' in info[name]:
                        t = info[name]['bases'][0]
                        target = [t.x, t.y]

        # if target is not None:
        #     print(self.team, target)
        #     # import matplotlib.pyplot as plt
        #     # fig, ax = plt.subplots()
        #     # ax.imshow(game_map.filled(fill_value=-1), origin='lower')
        #     # fig.savefig(f'map_{self.team}.png', bbox_inches='tight')
        #     # plt.close(fig)
        #     # print(info)
        #     # # input()

        if 'tanks' in myinfo:
            for tank in myinfo['tanks']:
                if tank.uid in self.previous_positions:
                    if all(tank.position == self.previous_positions[tank.uid]):
                        tank.set_heading(np.random.random() * 360.0)
                    elif target is not None:
                        # print('tank', tank['position'], 'going to', target)
                        tank.goto(*target)

                self.previous_positions[tank.uid] = tank.position

        if 'ships' in myinfo:
            for ship in myinfo['ships']:
                if ship.uid in self.previous_positions:
                    if all(ship.position == self.previous_positions[ship.uid]):
                        if ship.get_distance(ship.owner.x, ship.owner.y) > 20:
                            ship.convert_to_base()
                        else:
                            ship.set_heading(np.random.random() * 360.0)
                self.previous_positions[ship.uid] = ship.position

        if 'jets' in myinfo:
            for jet in myinfo['jets']:
                if target is not None:
                    jet.goto(*target)
