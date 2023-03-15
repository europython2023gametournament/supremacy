# SPDX-License-Identifier: BSD-3-Clause

import matplotlib as mpl
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from matplotlib.colors import Normalize

from . import config
from .tools import periodic_distances


class GameMap:

    def __init__(self, nx, ny, ng, high_contrast=False):

        self.nx = nx
        self.ny = ny
        self.ng = ng
        image = np.zeros([self.ny, self.nx])
        self.nseeds = 200
        self.xseed = np.random.randint(self.nx, size=self.nseeds)
        self.yseed = np.random.randint(self.ny, size=self.nseeds)

        image[(self.yseed, self.xseed)] = 10000

        smooth = gaussian_filter(image, sigma=30, mode='wrap')

        self.array = np.clip(smooth, 0, 1).astype(int)
        cmap = mpl.colormaps['terrain']
        norm = Normalize()
        if high_contrast:
            to_image = np.flipud(self.array * 255)
        else:
            to_image = cmap(norm(np.flipud(smooth))) * 255
        im = Image.fromarray(to_image.astype(np.uint8))
        im.save('background.png')

    def add_players(self, players):
        inds = np.random.choice(np.arange(self.nseeds),
                                size=len(players),
                                replace=False)
        locations = {}
        for n, player in enumerate(players):
            not_set = True
            while not_set:
                direction = np.random.randint(4)
                i = self.xseed[inds[n]]
                j = self.yseed[inds[n]]
                while self.array[j, i] > 0:
                    if direction == 0:
                        i = (i + 1) % self.nx
                    elif direction == 1:
                        i = (i - 1) % self.nx
                    elif direction == 2:
                        j = (j + 1) % self.ny
                    elif direction == 3:
                        j = (j - 1) % self.ny
                not_set = False
                for loc in locations.values():
                    dist = periodic_distances(i, j, loc[0], loc[1])[0].min()
                    if dist < 2 * config.competing_mine_radius:
                        not_set = True
            locations[player.team] = (i, j)

        return locations


class MapView:

    def __init__(self, array):
        self.array = array

    def __getitem__(self, inds):
        return self.array[inds]

    def __setitem__(self, inds, value):
        self.array[inds] = value

    def view(self, x, y, dx, dy):
        slices = self.view_slices(x, y, dx, dy)
        return [self.array[s[0], s[1]] for s in slices]

    def view_slices(self, x, y, dx, dy):
        ix = int(x)
        iy = int(y)
        ny, nx = self.array.shape
        xmin = ix - dx
        xmax = ix + dx + 1
        ymin = iy - dy
        ymax = iy + dy + 1
        slices = [(slice(max(ymin, 0), min(ymax, ny)), slice(max(xmin, 0),
                                                             min(xmax, nx)))]
        if (xmin < 0) and (ymin < 0):
            slices += [(slice(0, ymax), slice(nx + xmin, nx)),
                       (slice(ny + ymin, ny), slice(0, xmax)),
                       (slice(ny + ymin, ny), slice(nx + xmin, nx))]
        elif (xmin < 0) and (ymax >= ny):
            slices += [(slice(ymin, ny), slice(nx + xmin, nx)),
                       (slice(0, ymax - ny), slice(0, xmax)),
                       (slice(0, ymax - ny), slice(nx + xmin, nx))]
        elif (xmax >= nx) and (ymin < 0):
            slices += [(slice(0, ymax), slice(0, xmax - nx)),
                       (slice(ny + ymin, ny), slice(xmin, nx)),
                       (slice(ny + ymin, ny), slice(0, xmax - nx))]
        elif (xmax >= nx) and (ymax >= ny):
            slices += [(slice(0, ymax - ny), slice(xmin, nx)),
                       (slice(ymin, ny), slice(0, xmax - nx)),
                       (slice(0, ymax - ny), slice(0, xmax - nx))]
        elif xmin < 0:
            slices.append((slice(ymin, ymax), slice(nx + xmin, nx)))
        elif xmax >= nx:
            slices.append((slice(ymin, ymax), slice(0, xmax - nx)))
        elif ymin < 0:
            slices.append((slice(ny + ymin, ny), slice(xmin, xmax)))
        elif ymax >= ny:
            slices.append((slice(0, ymax - ny), slice(xmin, xmax)))
        return slices
