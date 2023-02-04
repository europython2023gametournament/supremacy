from PIL import Image
from matplotlib import colors
import numpy as np
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
        # self.graphics = graphics
        self.game_map = game_map
        self.bases = {}
        self.build_base(x=location[0], y=location[1])
        # self.tanks = {}
        # self.ships = {}
        # self.jets = {}
        # self.mines = {}
        # self.generate_images()

    # def generate_images(self):
    #     rgb = colors.to_rgb(f'C{self.number}')
    #     for f in ('jet', 'tank', 'ship', 'base'):
    #         img = Image.open(f'{f}.png')
    #         img = img.convert('RGBA')
    #         data = img.getdata()
    #         new_data = np.array(data).reshape(img.height, img.width, 4)
    #         for i in range(3):
    #             new_data[..., i] = int(round(rgb[i] * 255))
    #         out = Image.fromarray(new_data.astype(np.uint8))
    #         out.save(f'{f}_{self.number}.png')

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

        # import matplotlib.pyplot as plt
        # fig, ax = plt.subplots()
        # ax.imshow(self.game_map.filled(fill_value=-1), origin='lower')
        # fig.savefig(f'map_{self.number}.png', bbox_inches='tight')
        # plt.close(fig)
        # input()

    def build_base(self, x, y):
        uid = uuid.uuid4().hex
        self.bases[uid] = Base(x=x,
                               y=y,
                               team=self.team,
                               number=self.number,
                               batch=self.batch,
                               owner=self,
                               uid=uid)

    def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
        if safe:
            try:
                self.ai.exec(t=t, dt=dt, info=info, game_map=self.game_map)
            except:
                pass
        else:
            self.ai.exec(t=t, dt=dt, info=info, game_map=self.game_map)
        # if not safe:
        #     nprops = 0
        #     if self.ai.heading is not None:
        #         nprops += 1
        #     if self.ai.goto is not None:
        #         nprops += 1
        #     if self.ai.left is not None:
        #         nprops += 1
        #     if self.ai.right is not None:
        #         nprops += 1
        #     if nprops > 1:
        #         print('Warning, more than one AI property is set, '
        #               'results may be unpredictable!')
        # # try:
        # if self.ai.heading is not None:
        #     self.heading = self.ai.heading
        # if self.ai.goto is not None:
        #     self.goto(*self.ai.goto)
        # if self.ai.left is not None:
        #     self.left(self.ai.left)
        # if self.ai.right is not None:
        #     self.right(self.ai.right)
        # # except:
        # #     print('Error in ', self.ai.creator, self.name)
        # #     pass

    def collect_transformed_ships(self):
        for base in self.bases.values():
            for uid in base.transformed_ships:
                del base.ships[uid]
