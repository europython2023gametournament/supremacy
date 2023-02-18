import matplotlib as mpl
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
from matplotlib.colors import Normalize


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
            direction = np.random.randint(4)
            i = self.xseed[inds[n]]
            j = self.yseed[inds[n]]
            while self.array[j, i] > 0:
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
            locations[player.creator] = (i, j)

        return locations


class MapView:

    def __init__(self, array):
        self.array = array

    def __getitem__(self, inds):
        return self.array[inds]

    def __setitem__(self, inds, value):
        self.array[inds] = value

    def view(self, x, y, dx, dy):
        ix = int(x)
        iy = int(y)
        ny, nx = self.array.shape
        xmin = ix - dx
        xmax = ix + dx + 1
        ymin = iy - dy
        ymax = iy + dy + 1
        view = [self.array[max(ymin, 0):min(ymax, ny), max(xmin, 0):min(xmax, nx)]]
        if (xmin < 0) and (ymin < 0):
            view += [
                self.array[0:ymax, nx + xmin:nx], self.array[ny + ymin:ny, 0:xmax],
                self.array[ny + ymin:ny, nx + xmin:nx]
            ]
        elif (xmin < 0) and (ymax >= ny):
            view += [
                self.array[ymin:ny, nx + xmin:nx], self.array[0:ymax - ny, 0:xmax],
                self.array[0:ymax - ny, nx + xmin:nx]
            ]
        elif (xmax >= nx) and (ymin < 0):
            view += [
                self.array[0:ymax, 0:xmax - nx], self.array[ny + ymin:ny, xmin:nx],
                self.array[ny + ymin:ny, 0:xmax - nx]
            ]
        elif (xmax >= nx) and (ymax >= ny):
            view += [
                self.array[0:ymax - ny, xmin:nx], self.array[ymin:ny, 0:xmax - nx],
                self.array[0:ymax - ny, 0:xmax - nx]
            ]
        elif xmin < 0:
            view.append(self.array[ymin:ymax, nx + xmin:nx])
        elif xmax >= nx:
            view.append(self.array[ymin:ymax, 0:xmax - nx])
        elif ymin < 0:
            view.append(self.array[ny + ymin:ny, xmin:xmax])
        elif ymax >= ny:
            view.append(self.array[0:ymax - ny, xmin:xmax])
        return view
