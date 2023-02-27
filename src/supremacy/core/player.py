import pyglet
import uuid

from .. import config
from .base import Base
from .game_map import MapView


class Player:

    def __init__(self,
                 ai,
                 location,
                 number,
                 team,
                 batch,
                 game_map,
                 score,
                 nplayers,
                 base_locations,
                 high_contrast=False):
        self.ai = ai
        self.ai.team = team
        self.ai.number = number
        self.name = ai.creator
        self.hq = location
        self.number = number
        self.team = team
        self.batch = batch
        self.base_locations = base_locations
        self.game_map = MapView(game_map)
        self.bases = {}
        self.tanks = {}
        self.ships = {}
        self.jets = {}
        self.score = score
        self.high_contrast = high_contrast
        self.build_base(x=location[0], y=location[1])
        self.transformed_ships = []
        self.label = None
        self.nplayers = nplayers
        dx = 1500 // nplayers
        self.avatar = pyglet.sprite.Sprite(img=config.images[f'base_{self.number}'],
                                           x=(self.number * dx) + 180,
                                           y=config.ny + 12,
                                           batch=self.batch)

    def update_player_map(self, x, y):
        r = config.view_radius
        views = self.game_map.view(x=x, y=y, dx=r, dy=r)
        for view in views:
            view.mask = False

        # ix = int(x)
        # iy = int(y)
        # ny, nx = self.game_map.shape
        # xmin = ix - r
        # xmax = ix + r + 1
        # ymin = iy - r
        # ymax = iy + r + 1
        # self.game_map[max(ymin, 0):min(ymax, ny),
        #               max(xmin, 0):min(xmax, nx)].mask = False
        # if (xmin < 0) and (ymin < 0):
        #     self.game_map[0:ymax, nx + xmin:nx].mask = False
        #     self.game_map[ny + ymin:ny, 0:xmax].mask = False
        #     self.game_map[ny + ymin:ny, nx + xmin:nx].mask = False
        # elif (xmin < 0) and (ymax >= ny):
        #     self.game_map[ymin:ny, nx + xmin:nx].mask = False
        #     self.game_map[0:ymax - ny, 0:xmax].mask = False
        #     self.game_map[0:ymax - ny, nx + xmin:nx].mask = False
        # elif (xmax >= nx) and (ymin < 0):
        #     self.game_map[0:ymax, 0:xmax - nx].mask = False
        #     self.game_map[ny + ymin:ny, xmin:nx].mask = False
        #     self.game_map[ny + ymin:ny, 0:xmax - nx].mask = False
        # elif (xmax >= nx) and (ymax >= ny):
        #     self.game_map[0:ymax - ny, xmin:nx].mask = False
        #     self.game_map[ymin:ny, 0:xmax - nx].mask = False
        #     self.game_map[0:ymax - ny, 0:xmax - nx].mask = False
        # elif xmin < 0:
        #     self.game_map[ymin:ymax, nx + xmin:nx].mask = False
        # elif xmax >= nx:
        #     self.game_map[ymin:ymax, 0:xmax - nx].mask = False
        # elif ymin < 0:
        #     self.game_map[ny + ymin:ny, xmin:xmax].mask = False
        # elif ymax >= ny:
        #     self.game_map[0:ymax - ny, xmin:xmax].mask = False

    def build_base(self, x, y):
        uid = uuid.uuid4().hex
        self.bases[uid] = Base(x=x,
                               y=y,
                               team=self.team,
                               number=self.number,
                               batch=self.batch,
                               owner=self,
                               uid=uid,
                               high_contrast=self.high_contrast)
        self.base_locations[int(y), int(x)] = 1

    def init_dt(self, dt):
        # self.make_label()
        self.transformed_ships.clear()
        # for v in self.vehicles:
        #     v.cooldown = max(v.cooldown - dt, 0)

    def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
        if safe:
            try:
                self.ai.run(t=t, dt=dt, info=info,
                            game_map=self.game_map)  # game_map.array.filled(-1)
            except:
                pass
        else:
            self.ai.run(t=t, dt=dt, info=info,
                        game_map=self.game_map)  # game_map.array.filled(-1)

    def collect_transformed_ships(self):
        for uid in self.transformed_ships:
            del self.ships[uid]

    @property
    def children(self):
        return list(self.bases.values()) + self.vehicles

    @property
    def vehicles(self):
        return list(self.tanks.values()) + list(self.ships.values()) + list(
            self.jets.values())

    def remove(self, uid):
        if uid in self.tanks:
            self.tanks[uid].delete()
            del self.tanks[uid]
        elif uid in self.ships:
            self.ships[uid].delete()
            del self.ships[uid]
        elif uid in self.jets:
            self.jets[uid].delete()
            del self.jets[uid]
        else:
            for base in self.bases.values():
                if uid in base.mines:
                    del base.mines[uid]
                    base.make_label()

    def remove_base(self, uid):
        self.bases[uid].delete()
        del self.bases[uid]

    def economy(self):
        return int(sum([base.crystal for base in self.bases.values()]))

    def make_label(self):
        # if self.label is not None:
        #     self.label.delete()
        # economy = int(sum([base.crystal for base in self.bases.values()]))
        # self.label = pyglet.text.Label(f'{self.name}: {economy} [{self.score}]',
        #                                color=(255, 255, 255, 255),
        #                                font_size=min(14, 100 / self.nplayers),
        #                                x=self.avatar.x + 15,
        #                                y=self.avatar.y - 7,
        #                                batch=self.batch)
        return f'{self.economy()} [{self.score}]'.rjust(15)

    def rip(self):
        for v in self.vehicles:
            v.delete()
        self.tanks.clear()
        self.ships.clear()
        self.jets.clear()
        self.avatar.delete()
        self.label.delete()

    def dump_map(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.imshow(self.game_map.array, origin='lower')
        fig.savefig(f'{self.name}_map.png', bbox_inches='tight')
