import numpy as np

class Rampup:

    def __init__(self, frequency, maxloop):

        self.maxloop = maxloop
        self.frequency = frequency

        self.reset()

        return

    def reset(self):

        rep = int(self.maxloop / self.frequency)
        rep2 = int(self.frequency / 3) + 1
        self.ramp = ([0] * rep2 + list(np.linspace(0.2, 1, rep2, endpoint=False)) + list(np.linspace(1, 0.2, rep2 ))) * rep
        rep = int(self.maxloop / self.frequency)
        rep2 = int(self.frequency / 2) + 1
        self.ramp = ([0] * rep2 + list(np.linspace(1, 0.2, rep2))) * rep
        self.ramp = 10 * [0] + list(np.linspace(1, 0.2, self.frequency))

        self.ramp = (rep2 * [0] + rep2 * [0.55] ) *rep

        self.ramp = int(1 + (1 * self.frequency) / 2) * [0.0] + list(np.linspace(0.65, 0.55, int(self.frequency / 2) + 1, endpoint=True))
        self.ramp = int(1 + (2 * self.frequency) / 3) * [0.0] + int(1 + (1 * self.frequency) / 3) * [0.53]

    def run(self):

        throttle = self.ramp.pop()
        print('throttle = ', throttle)

        return 0.0, throttle
