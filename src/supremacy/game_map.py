import ipywidgets as ipw
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib import cm
from scipy.stats import multivariate_normal

class GameMap:

    def __init__(self):

        nclusters = 200
        npercluster = 10000

        # position = np.zeros((nclusters, npercluster, 2))

        n_t = 1000
        n_p = 2000
        image = np.zeros([n_t, n_p])

        tmin = 0
        tmax = np.pi
        pmin = 0
        pmax = 2 * np.pi
        dt = (tmax - tmin) / n_t
        dp = (pmax - pmin) / n_p

        tpos = np.linspace(tmin + 0.5*dt, tmax - 0.5*dt, n_t)
        ppos = np.linspace(pmin + 0.5*dp, pmax - 0.5*dp, n_p)
        # pe = np.linspace(0, 2*np.pi, n_p+1)

        pgrid, tgrid = np.meshgrid(ppos, tpos)
        pos = np.dstack((pgrid, tgrid))

        r = 0.05 * np.pi
        rt = int(r/dt)
        rp = int(r/dp)
        print(dt, r, rt)

        for n in range(nclusters):
        print(n)
        # dt = np.random.normal(scale=np.random.random() * 0.1 * np.pi, size=npercluster)
        # dp = np.random.normal(scale=np.random.random() * 0.1 * 2 * np.pi, size=npercluster)
        # dt = np.random.normal(scale=0.02 * np.pi, size=npercluster)
        # dp = np.random.normal(scale=0.02 * 2 * np.pi, size=npercluster)

        theta = np.random.random() * np.pi
        phi = np.random.random() * 2 * np.pi

        #     sigma = 0.5 * game_info.config["ships"][ship_class][
        #         'base_view_range'] + (view_penalty *
        #                               int(self.speed_index == 3))

        #     yy = stats.norm.pdf(x, ypos, sigma)

        # it = int(theta / dt)
        # t0 = it - rt
        # t1 = it + rt
        # ip = int(phi / dp)
        # p0 = ip - rp
        # p1 = ip + rp
        # # print(t0, t1, p0, p1)
        # for i in range(max(p0, 0), min(p1+1, n_p)):
        #     for j in range(max(t0, 0), min(t1+1, n_t)):
        #         dist = np.sqrt((i-ip)**2 + (j-it)**2)
        #         if dist <= rt:
        #             image[j, i] += 1

        h = multivariate_normal.pdf(pos, [phi, theta], 0.002 * np.pi)
        # h, xedges, yedges = np.histogram2d(theta, phi, bins=(te, pe))
        image += h

        # im = image / image.max() *
        im = np.clip(image, 0, 6)
        im = (im / im.max() * 1).astype(int)
        fig, ax = plt.subplots()
        # new_map = cm.gray.from_list('whatever', ('white', 'black'), N=512)
        ax.imshow(im, origin='lower', cmap='terrain', aspect='equal')
        fig.show()
