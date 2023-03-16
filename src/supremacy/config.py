# SPDX-License-Identifier: BSD-3-Clause

from matplotlib import colors
import numpy as np
from PIL import Image
import pyglet
import os


def _load_image(path):
    img = pyglet.image.load(path)
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img


class Config:

    def __init__(self):

        self.speed = {'tank': 10, 'ship': 5, 'jet': 20, 'base': 0}
        self.health = {'tank': 50, 'ship': 80, 'jet': 50, 'base': 100, 'mine': 50}
        self.attack = {'tank': 20, 'ship': 10, 'jet': 30, 'base': 0, 'mine': 0}
        self.cost = {'tank': 500, 'ship': 2000, 'jet': 4000, 'mine': 1000}
        self.view_radius = 20
        self.vehicle_offset = 5
        self.competing_mine_radius = 40
        self.fight_radius = 5
        self.nx = 1920
        self.ny = 992
        self.resource_path = os.path.join('..', 'resources')
        self.images = {
            'explosion': _load_image(os.path.join(self.resource_path, 'explosion.png'))
        }

    def generate_images(self, nplayers):
        for n in range(nplayers):
            rgb = colors.to_rgb(f'C{n}')
            for name in ('jet', 'ship', 'tank', 'base', 'skull'):
                fname = os.path.join(self.resource_path, f'{name}.png')
                img = Image.open(fname)
                img = img.convert('RGBA')
                data = img.getdata()
                new_data = np.array(data).reshape(img.height, img.width, 4)
                for i in range(3):
                    new_data[..., i] = int(round(rgb[i] * 255))
                out = Image.fromarray(new_data.astype(np.uint8))
                outfile = os.path.join(self.resource_path, f'{name}_{n}.png')
                out.save(outfile)
                self.images[f'{name}_{n}'] = _load_image(outfile)
