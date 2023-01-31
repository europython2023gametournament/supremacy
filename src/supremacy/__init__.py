from matplotlib import colors
import numpy as np
from PIL import Image
import pyglet


class Config:

    def __init__(self):

        self.speed = {'tank': 20, 'ship': 60, 'jet': 60}
        self.health = {'tank': 70, 'ship': 100, 'jet': 100}
        self.attack = {'tank': 20, 'ship': 30, 'jet': 0}
        self.cost = {'tank': 200, 'ship': 1000, 'jet': 400, 'mine': 500}
        self.images = {}

    def generate_images(self, nplayers):
        for n in range(nplayers):
            rgb = colors.to_rgb(f'C{n}')
            for name in ('jet', 'ship', 'tank'):
                print(n, name)
                img = Image.open(f'{name}.png')
                img = img.convert('RGBA')
                data = img.getdata()
                new_data = np.array(data).reshape(img.height, img.width, 4)
                for i in range(3):
                    new_data[..., i] = int(round(rgb[i] * 255))
                out = Image.fromarray(new_data.astype(np.uint8))
                out.save(f'{name}_{n}.png')
                image = pyglet.image.load(f'{name}_{n}.png')
                image.anchor_x = image.width // 2
                image.anchor_y = image.height // 2
                self.images[f'{name}_{n}'] = image
        print(self.images)


config = Config()
