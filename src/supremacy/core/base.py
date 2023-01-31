import pythreejs as p3
import uuid

from .vehicles import Tank


class Base:

    def __init__(self, x, y, team, color, graphics):
        self.x = x
        self.y = y
        self.team = team
        self.color = color
        self.tanks = {}
        self.ships = {}
        self.jets = {}
        self.mines = 1
        self.crystal = 0
        self.graphics = graphics
        # self.draw_base()

    def draw_base(self):
        size = 15
        geom = p3.SphereGeometry(radius=size, widthSegments=8, heightSegments=6)
        mat = p3.MeshBasicMaterial(color=self.color)
        self.graphics.add(
            p3.Mesh(geometry=geom, material=mat, position=[self.x, self.y, 0]))

    @property
    def vehicles(self):
        return list(self.tanks.values()) + list(self.ships.values()) + list(
            self.jets.values())

    def build_mine(self):
        self.mines += 1

    def build_tank(self, heading, batch):
        vid = uuid.uuid4()
        self.tanks[vid] = Tank(x=self.x + 5,
                               y=self.y + 5,
                               color=self.color,
                               team=self.team,
                               heading=heading,
                               batch=batch)
        self.crystal -= self.tanks[vid].cost
        # self.graphics.add(self.tanks[vid].avatar)
