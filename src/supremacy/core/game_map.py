import ipywidgets as ipw
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib import cm
from scipy.ndimage import gaussian_filter
from PIL import Image
from matplotlib.colors import Normalize


class GameMap:

    def __init__(self, nx, ny, ng):

        self.nx = nx
        self.ny = ny
        self.ng = ng
        image = np.zeros([self.nx, self.ny])
        n = 200
        x = np.random.randint(self.nx, size=n)
        y = np.random.randint(self.ny, size=n)

        for i in range(n):
            image[x[i], y[i]] = 10000

        smooth = gaussian_filter(image, sigma=30)

        self.array = np.clip(smooth, 0, 1).astype(int)
        cmap = mpl.colormaps['terrain']
        norm = Normalize()
        im = Image.fromarray((cmap(norm(smooth.T)) * 255).astype(np.uint8))
        im.save('background.png')

    def add_players(self, players):
        return
