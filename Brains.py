import numpy as np
from scipy import interpolate
default_path = 'grid_coordinates.csv'


class Brains:

    def __init__(self, **kwargs):
        # need to initialize some stuff

        try:
            path = kwargs['pic_to_reality_csv']
            self.pic_mapx, self.pic_mapy = get_maps_from_file(path)

        except:
            self.pic_mapx, self.pic_mapy = get_maps_from_file(default_path)

        return

    def run(self, bbox):

        bbox = []
        print('in brains')
        print(bbox)
        throttle = 0.3

        emily = False
        emil = True
        angle, x, y = self.path_planning(bbox)
        if y == 0.0:
            runtime = 0.5
            throttle = 1.0
            angle = -0.5
            print('y==0', runtime, throttle)
#            throttle = 0.7
        elif  np.sqrt(x*x + y*y) < 30.0:
            print('I\'m there! Emil take over please!')
            emily = False
            emil = True
            runtime = 0.0
        elif np.sqrt(x*x + y*y) < 40.0:
            runtime = 0.1
        elif np.sqrt(x*x + y*y) < 60.0:
            runtime = 0.3
        waittime = 1.0

        return angle, throttle, runtime, waittime, emily, emil, x, y, emil3, 1.0

    def path_planning(self, bbox):

        if len(bbox) == 0:
            return 0.0, 0.0, 0.0
        # idx = np.argmax(bbox[:,0])
        # xpic = bbox[idx, 1]
        # ypic = bbox[idx, 2]

        xpic = bbox[0][2]
        ypic = bbox[0][3]
        print('xpic ', xpic, 'ypic', ypic)

        x, y = self.pictoreal(xpic, ypic)

        if np.isnan(x) or np.isnan(y):
            print('got nans')
            x = 0.0
            y = 0.0
            if xpic > .8:
                angle = 0.2
            if xpic < 0.2:
                angle = -0.2
            angle = 0.0
            diameter = 0.0
        else:
            diameter = (x * x + y * y) / x
            angle = self.diatoangle(diameter)
        print('x ', x, 'y ', y)
        print('diameter ', diameter, 'angle ', angle)

        return angle, x, y

    def pictoreal(self, xpic, ypic):

        xy = np.array([xpic, ypic])
        x = self.pic_mapx(xy)
        y = self.pic_mapy(xy)

        return x, y

    def diatoangle(self, diameter):

        factor = 1.0
        if diameter < 0:
            factor = -1.0

        if abs(diameter) < 140:
            return 1.0 * factor
        if abs(diameter) < 165:
            return 0.9 * factor
        if abs(diameter) < 195:
            return 0.8 * factor
        if abs(diameter) < 220:
            return 0.7 * factor
        if abs(diameter) < 260:
            return 0.6 * factor
        if abs(diameter) < 320:
            return 0.5 * factor
        if abs(diameter) < 400:
            return 0.4 * factor
        if abs(diameter) < 550:
            return 0.3 * factor
        if abs(diameter) < 720:
            return 0.2 * factor
        if abs(diameter) < 1020:
            return 0.1 * factor

        return 0.0


def get_maps_from_file(path):

    x = np.genfromtxt(path, delimiter=',')
    zx = x[1:, 0]
    zy = x[1:, 1]
    xy = np.zeros((len(zx), 2))
    xy[:, 0] = x[1:, 2]
    xy[:, 1] = x[1:, 4]
    assert (not np.isnan(xy.any()))
    assert (not np.isnan(zy.any()))
    assert (not np.isnan(zx.any()))
    xy[:, 0] = xy[:, 0] / x[0, 0]
    xy[:, 1] = xy[:, 1] / x[0, 1]
    mapx = interpolate.CloughTocher2DInterpolator(xy, zx)
    mapy = interpolate.CloughTocher2DInterpolator(xy, zy)

    return mapx, mapy
