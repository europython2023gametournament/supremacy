import uuid

from .. import config
from .base import Base


class Player:

    def __init__(self, ai, location, number, team, batch, game_map):
        self.ai = ai
        self.ai.team = team
        self.ai.number = number
        self.name = ai.creator
        self.hq = location
        self.number = number
        self.team = team
        self.batch = batch
        self.game_map = game_map
        self.bases = {}
        self.tanks = {}
        self.ships = {}
        self.jets = {}
        self.build_base(x=location[0], y=location[1])
        self.score = 0
        self.transformed_ships = []

    def update_player_map(self, x, y):
        r = config.view_radius
        ix = int(x)
        iy = int(y)
        ny, nx = self.game_map.shape
        xmin = ix - r
        xmax = ix + r + 1
        ymin = iy - r
        ymax = iy + r + 1
        self.game_map[max(ymin, 0):min(ymax, ny),
                      max(xmin, 0):min(xmax, nx)].mask = False
        if (xmin < 0) and (ymin < 0):
            self.game_map[0:ymax, nx + xmin:nx].mask = False
            self.game_map[ny + ymin:ny, 0:xmax].mask = False
            self.game_map[ny + ymin:ny, nx + xmin:nx].mask = False
        elif (xmin < 0) and (ymax >= ny):
            self.game_map[ymin:ny, nx + xmin:nx].mask = False
            self.game_map[0:ymax - ny, 0:xmax].mask = False
            self.game_map[0:ymax - ny, nx + xmin:nx].mask = False
        elif (xmax >= nx) and (ymin < 0):
            self.game_map[0:ymax, 0:xmax - nx].mask = False
            self.game_map[ny + ymin:ny, xmin:nx].mask = False
            self.game_map[ny + ymin:ny, 0:xmax - nx].mask = False
        elif (xmax >= nx) and (ymax >= ny):
            self.game_map[0:ymax - ny, xmin:nx].mask = False
            self.game_map[ymin:ny, 0:xmax - nx].mask = False
            self.game_map[0:ymax - ny, 0:xmax - nx].mask = False
        elif xmin < 0:
            self.game_map[ymin:ymax, nx + xmin:nx].mask = False
        elif xmax >= nx:
            self.game_map[ymin:ymax, 0:xmax - nx].mask = False
        elif ymin < 0:
            self.game_map[ny + ymin:ny, xmin:xmax].mask = False
        elif ymax >= ny:
            self.game_map[0:ymax - ny, xmin:xmax].mask = False

    def build_base(self, x, y):
        uid = uuid.uuid4().hex
        self.bases[uid] = Base(x=x,
                               y=y,
                               team=self.team,
                               number=self.number,
                               batch=self.batch,
                               owner=self,
                               uid=uid)

    def init_dt(self, dt):
        self.transformed_ships.clear()
        # for v in self.vehicles:
        #     v.cooldown = max(v.cooldown - dt, 0)

    def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
        if safe:
            try:
                self.ai.exec(t=t, dt=dt, info=info, game_map=self.game_map)
            except:
                pass
        else:
            self.ai.exec(t=t, dt=dt, info=info, game_map=self.game_map)

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
        # elif uid in self.bases:
        #     self.bases[uid].avatar.delete()
        #     del self.bases[uid]
        else:
            for base in self.bases.values():
                if uid in base.mines:
                    del base.mines[uid]
                    base.make_label()
        # elif uid in self.uid:
        #     self.avatar.delete()
        #     del self.owner.bases[uid]

    def remove_base(self, uid):
        self.bases[uid].delete()
        del self.bases[uid]
