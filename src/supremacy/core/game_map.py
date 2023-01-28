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
        self.nseeds = 200
        self.xseed = np.random.randint(self.nx, size=self.nseeds)
        self.yseed = np.random.randint(self.ny, size=self.nseeds)

        image[(self.xseed, self.yseed)] = 10000

        # for i in range(self.nseeds):
        #     image[self.xseed[i], self.yseed[i]] = 10000

        smooth = gaussian_filter(image, sigma=30, mode='wrap')

        self.array = np.clip(smooth, 0, 1).astype(int)
        cmap = mpl.colormaps['terrain']
        norm = Normalize()
        im = Image.fromarray((cmap(norm(smooth.T)) * 255).astype(np.uint8))
        im.save('background.png')

    def add_players(self, players):
        inds = np.random.randint(self.nseeds, size=len(players), replace=False)
        for i, player in enumerate(players):
            print(player)

        return
