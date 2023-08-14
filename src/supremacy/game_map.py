# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, List

import matplotlib as mpl
import numpy as np
from matplotlib.colors import Normalize
from PIL import Image
import pyglet
from scipy.ndimage import gaussian_filter

from . import config
from .config import scale_image
from .tools import periodic_distances, wrap_position


class GameMap:
    def __init__(self, nx: int, ny: int, high_contrast: bool = False):
        self.nx = nx
        self.ny = ny
        image = np.zeros([self.ny, self.nx])
        self.nseeds = int((nx * ny) * 200 / (1920 * 1080))
        self.xseed = np.random.randint(self.nx, size=self.nseeds)
        self.yseed = np.random.randint(self.ny, size=self.nseeds)

        image[(self.yseed, self.xseed)] = 10000

        smooth = gaussian_filter(image, sigma=30, mode="wrap")

        self.array = np.clip(smooth, 0, 1).astype(int)
        cmap = mpl.colormaps["terrain"]
        norm = Normalize()
        if high_contrast:
            to_image = np.flipud(self.array * 255)
            to_image = np.broadcast_to(
                to_image.reshape(to_image.shape + (1,)), to_image.shape + (3,)
            )
        else:
            gy, gx = np.gradient(np.flipud(self.array))
            contour = np.abs(gy) + np.abs(gx)
            inds = contour > 0
            ii = np.broadcast_to(inds.reshape(inds.shape + (1,)), inds.shape + (3,))
            to_image = cmap(norm(np.flipud(smooth)))[..., :3] * 255
            contour_color = np.full_like(to_image, (0, 140, 240))
            to_image[ii] = contour_color[ii]

        img = scale_image(Image.fromarray(to_image.astype(np.uint8)), config.scaling)
        self.background_image = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGB",
            data=img.tobytes(),
            pitch=-img.width * 3,
        )

    def add_players(self, players: dict):
        inds = np.random.choice(
            np.arange(self.nseeds), size=len(players), replace=False
        )
        locations = {}
        niter = 0
        for n, player in enumerate(players):
            not_set = True
            while not_set:
                niter += 1
                if niter > 500:
                    raise RuntimeError("Could not find a suitable location for a base")
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
                # Check for lakes
                if not not_set:
                    # Ray-trace from (i, j) in 64 directions and find maximum distance
                    # to land (array value of 1)
                    thetas = np.linspace(0, 2 * np.pi, 64)
                    vectors = np.array([np.sin(thetas), np.cos(thetas)]).T
                    distance = np.linspace(0, config.ny, config.ny)
                    rays = vectors.reshape(vectors.shape + (1,)) * distance
                    rays[:, 0, :] += j
                    rays[:, 1, :] += i
                    x, y = wrap_position(
                        rays[:, 1, :].astype(int), rays[:, 0, :].astype(int)
                    )
                    map_values = self.array[y, x]
                    max_dists = np.argmax(map_values, axis=1)
                    max_map_values = np.max(map_values, axis=1)
                    w = np.where(max_map_values == 1)
                    distmax = max_dists[w].max()
                    if distmax < 100:
                        not_set = True

            locations[player] = (i, j)

        return locations


class MapView:
    def __init__(self, array: np.ndarray):
        self.array = array

    def __getitem__(self, inds: Any) -> np.ndarray:
        return self.array[inds]

    def __setitem__(self, inds: Any, value: Any):
        self.array[inds] = value

    def view(self, x: float, y: float, dx: int, dy: int) -> List[np.ndarray]:
        slices = self.view_slices(x, y, dx, dy)
        return [self.array[s[0], s[1]] for s in slices]

    def view_slices(self, x: float, y: float, dx: int, dy: int) -> List[slice]:
        ix = int(x)
        iy = int(y)
        ny, nx = self.array.shape
        xmin = ix - dx
        xmax = ix + dx + 1
        ymin = iy - dy
        ymax = iy + dy + 1
        slices = [
            (slice(max(ymin, 0), min(ymax, ny)), slice(max(xmin, 0), min(xmax, nx)))
        ]
        if (xmin < 0) and (ymin < 0):
            slices += [
                (slice(0, ymax), slice(nx + xmin, nx)),
                (slice(ny + ymin, ny), slice(0, xmax)),
                (slice(ny + ymin, ny), slice(nx + xmin, nx)),
            ]
        elif (xmin < 0) and (ymax >= ny):
            slices += [
                (slice(ymin, ny), slice(nx + xmin, nx)),
                (slice(0, ymax - ny), slice(0, xmax)),
                (slice(0, ymax - ny), slice(nx + xmin, nx)),
            ]
        elif (xmax >= nx) and (ymin < 0):
            slices += [
                (slice(0, ymax), slice(0, xmax - nx)),
                (slice(ny + ymin, ny), slice(xmin, nx)),
                (slice(ny + ymin, ny), slice(0, xmax - nx)),
            ]
        elif (xmax >= nx) and (ymax >= ny):
            slices += [
                (slice(0, ymax - ny), slice(xmin, nx)),
                (slice(ymin, ny), slice(0, xmax - nx)),
                (slice(0, ymax - ny), slice(0, xmax - nx)),
            ]
        elif xmin < 0:
            slices.append((slice(ymin, ymax), slice(nx + xmin, nx)))
        elif xmax >= nx:
            slices.append((slice(ymin, ymax), slice(0, xmax - nx)))
        elif ymin < 0:
            slices.append((slice(ny + ymin, ny), slice(xmin, xmax)))
        elif ymax >= ny:
            slices.append((slice(0, ymax - ny), slice(xmin, xmax)))
        return slices
