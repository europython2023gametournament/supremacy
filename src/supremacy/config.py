# SPDX-License-Identifier: BSD-3-Clause

from matplotlib import colors
import numpy as np
from PIL import Image
import pyglet
import importlib_resources as ir


def _recenter_image(img):
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
        self.resources = ir.files('supremacy') / 'resources'
        img = _recenter_image(pyglet.image.load(self.resources / 'explosion.png'))
        self.images = {'explosion': img}

    def generate_images(self, nplayers):
        for n in range(nplayers):
            rgb = colors.to_rgb(f'C{n}')
            for name in ('jet', 'ship', 'tank', 'base', 'skull'):
                img = Image.open(self.resources / f'{name}.png')
                img = img.convert('RGBA')
                data = img.getdata()
                new_data = np.array(data).reshape(img.height, img.width, 4)
                for i in range(3):
                    new_data[..., i] = int(round(rgb[i] * 255))
                temp_image = Image.fromarray(new_data.astype(np.uint8))
                self.images[f'{name}_{n}'] = _recenter_image(
                    pyglet.image.ImageData(width=temp_image.width,
                                           height=temp_image.height,
                                           fmt='RGBA',
                                           data=temp_image.tobytes(),
                                           pitch=-temp_image.width * 4))
