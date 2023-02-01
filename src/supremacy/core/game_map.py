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
        image = np.zeros([self.ny, self.nx])
        self.nseeds = 200
        self.xseed = np.random.randint(self.nx, size=self.nseeds)
        self.yseed = np.random.randint(self.ny, size=self.nseeds)

        image[(self.yseed, self.xseed)] = 10000

        # for i in range(self.nseeds):
        #     image[self.xseed[i], self.yseed[i]] = 10000

        smooth = gaussian_filter(image, sigma=30, mode='wrap')

        self.array = np.clip(smooth, 0, 1).astype(int)
        cmap = mpl.colormaps['terrain']
        norm = Normalize()
        # im = Image.fromarray((cmap(norm(smooth)) * 255).astype(np.uint8))
        im = Image.fromarray(np.flipud(self.array * 255).astype(np.uint8))
        # .resize(
        #     (self.nx - 19, self.ny - 19))
        # im.resize((self.nx - 20, self.ny - 20))
        im.save('background.png')

    def add_players(self, players):
        inds = np.random.choice(np.arange(self.nseeds),
                                size=len(players),
                                replace=False)
        # graphics.pen.showturtle()
        # print(inds)
        # print(self.xseed)
        # print(self.yseed)
        locations = {}
        for n, player in enumerate(players):
            direction = np.random.randint(4)
            # val = self.array[self.xseed[inds[n]], self.yseed[inds[n]]]
            i = self.xseed[inds[n]]
            j = self.yseed[inds[n]]
            # graphics.pen.penup()
            # graphics.pen.goto(i, j)
            # graphics.pen.pendown()
            while self.array[j, i] > 0:
                # input()
                # print(n, i, j, self.array[j, i])
                if direction == 0:
                    i += 1
                    if i >= self.nx:
                        i = 0
                elif direction == 1:
                    i -= 1
                    if i < 0:
                        i = self.nx - 1
                elif direction == 2:
                    j += 1
                    if j >= self.ny:
                        j = 0
                elif direction == 3:
                    j -= 1
                    if j < 0:
                        j = self.ny - 1
            #     # graphics.pen.goto(i, j)
            # # print('edge found', i, j, self.array[j, i])
            # for ii in range(i - 1, i + 2):
            #     for jj in range(j - 1, j + 2):
            #         self.array[jj, ii] = 10 + n
            # # graphics.pen.penup()
            # # graphics.draw_base_star(x=i, y=j, n=n)
            locations[player.creator] = (i, j)

        return locations
