from PIL import Image
from matplotlib import colors
import numpy as np

from .base import Base


class Player:

    def __init__(self, ai, location, number, team, graphics, game_map):
        self.ai = ai
        self.ai.team = team
        self.ai.number = number
        self.name = ai.creator
        self.hq = location
        self.number = number
        self.team = team
        self.graphics = graphics
        self.game_map = game_map
        self.bases = [
            Base(x=location[0],
                 y=location[1],
                 team=team,
                 number=number,
                 graphics=self.graphics)
        ]
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

    def execute_ai(self, t: float, dt: float, info: dict, batch, safe: bool = False):
        if safe:
            try:
                self.ai.exec(t=t, dt=dt, info=info, batch=batch)
            except:
                pass
        else:
            self.ai.exec(t=t, dt=dt, info=info, batch=batch)
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
