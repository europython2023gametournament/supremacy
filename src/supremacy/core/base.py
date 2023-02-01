import pyglet
import uuid

from .. import config
from .vehicles import Tank, Ship, Jet


class Base:

    def __init__(self, x, y, team, number, batch, owner):
        self.x = x
        self.y = y
        self.team = team
        self.number = number
        self.owner = owner
        self.tanks = {}
        self.ships = {}
        self.jets = {}
        self.transformed_ships = []
        self.mines = 1
        self.crystal = 0
        # self.graphics = graphics
        # self.draw_base()
        self.owner.update_player_map(x=self.x, y=self.y)
        self.avatar = pyglet.sprite.Sprite(img=config.images[f'base_{self.number}'],
                                           x=self.x,
                                           y=self.y,
                                           batch=batch)

        ix = int(x)
        iy = int(y)
        dx = config.vehicle_offset
        offset = None
        while (offset is None):
            if self.owner.game_map[iy + dx, ix + dx] == 1:
                offset = (dx, dx)
            elif self.owner.game_map[iy - dx, ix + dx] == 1:
                offset = (dx, -dx)
            elif self.owner.game_map[iy + dx, ix - dx] == 1:
                offset = (-dx, dx)
            elif self.owner.game_map[iy - dx, ix - dx] == 1:
                offset = (-dx, -dx)
            else:
                dx += 1
        self.tank_offset = offset

        dx = config.vehicle_offset
        offset = None
        while (offset is None):
            if self.owner.game_map[iy + dx, ix + dx] == 0:
                offset = (dx, dx)
            elif self.owner.game_map[iy - dx, ix + dx] == 0:
                offset = (dx, -dx)
            elif self.owner.game_map[iy + dx, ix - dx] == 0:
                offset = (-dx, dx)
            elif self.owner.game_map[iy - dx, ix - dx] == 0:
                offset = (-dx, -dx)
            else:
                dx += 1
        self.ship_offset = offset

    # def draw_base(self):
    #     size = 15
    #     geom = p3.SphereGeometry(radius=size, widthSegments=8, heightSegments=6)
    #     mat = p3.MeshBasicMaterial(color=self.color)
    #     self.graphics.add(
    #         p3.Mesh(geometry=geom, material=mat, position=[self.x, self.y, 0]))

    @property
    def vehicles(self):
        return list(self.tanks.values()) + list(self.ships.values()) + list(
            self.jets.values())

    def init_dt(self):
        self.transformed_ships.clear()

    def build_mine(self):
        self.mines += 1
        self.crystal -= config.cost['mine']
        print('Building mine')

    def build_tank(self, heading, batch):
        print('Building tank')
        vid = uuid.uuid4().hex
        self.tanks[vid] = Tank(x=self.x + self.tank_offset[0],
                               y=self.y + self.tank_offset[1],
                               team=self.team,
                               number=self.number,
                               heading=heading,
                               batch=batch,
                               owner=self,
                               vid=vid)
        self.crystal -= config.cost['tank']
        # self.graphics.add(self.tanks[vid].avatar)

    def build_ship(self, heading, batch):
        print('Building ship')
        vid = uuid.uuid4().hex
        self.ships[vid] = Ship(x=self.x + self.ship_offset[0],
                               y=self.y + self.ship_offset[1],
                               team=self.team,
                               number=self.number,
                               heading=heading,
                               batch=batch,
                               owner=self,
                               vid=vid)
        self.crystal -= config.cost['ship']
        # self.graphics.add(self.tanks[vid].avatar)
