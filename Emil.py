import math
import time
import Adafruit_PCA9685


class Emil:

    reset = [1.6, 0.8, 1, 1]

    def __init__(self, channels, address, frequency=50, busnum=None):

        print('initialize Emil')
        # need to initialize some stuff
        self.channels = channels
        self.motorpositions = [0] * len(channels)
        self.pwm = Adafruit_PCA9685.PCA9685(address=address)
        self.pwm.set_pwm_freq(frequency)

        if busnum is not None:
            from Adafruit_GPIO import I2C
            # replace the get_bus function with our own
            def get_bus():
                return busnum
            I2C.get_default_bus = get_bus

        return

    def run(self, x, y):

        R, theta = self.radial(x, y)

        if R > 30:
            print("cigarette out of reach")

        else:
            positions = self.motors(x, y)
            print(R)
            print(theta)
            print(positions)

            for i in range(len(positions)):
                self.moveslow(self.channels[i], positions[i])
                self.set_servo_pulse(self.channels[i], positions[i])
                time.sleep(0.5)

            time.sleep(1)

            for i in range(len(self.reset)):
                self.moveslow(i, self.reset[i])
                self.set_servo_pulse(self.channels[i], self.reset[i])
                time.sleep(0.5)

        return

    def set_servo_pulse(self, channel, pulse):
        self.motorpositions[channel] = pulse
        pulse_length = 1000000
        pulse_length /= 50
        #   print('{0}us per period'.format(pulse_length))
        pulse_length /= 4096
        #   print('{0}us per bit'.format(pulse_length))
        pulse *= 1000
        #   print(pulse_length)
        pulse /= pulse_length
        #   print(pulse)
        pulse = round(pulse)
        #   print(pulse)
        pulse = int(pulse)
        #   print (pulse)
        self.pwm.set_pwm(channel, 0, pulse)
        print(self.motorpositions)

    def moveslow(self, channel, pulse):

        if (self.motorpositions[channel] - pulse) > 0:
            step = -0.01
        else:
            step = 0.01

        loop = True
        while loop:
            if abs(self.motorpositions[channel] - pulse) < 0.0001:
                loop = False
            else:
                self.set_servo_pulse(channel, self.motorpositions[channel] + step)
            time.sleep(0.05)

    def motors(self, x, y):

        signal = [0, 0, 0, 0]

        calibrationdistance = [(32, 1.48, 1, 1.05),
                               (30, 1.4, 1, 1),
                               (28, 1.3, 0.9, 1),
                               (26, 1.28, 0.73, 1),
                               (24, 1.2, 0.63, 1),
                               (22, 1.12, 0.52, 1),
                               (20, 1.08, 0.48, 1),
                               (18, 1, 0.4, 0.95),
                               (16, 0.95, 0.4, 0.86),
                               (14, 0.92, 0.4, 0.71),
                               (12, 0.9, 0.4, 0.71),
                               (10, 0.88, 0.4, 0.66),
                               ]

        R, theta = self.radial(x, y)

        signal[0] = round(-0.5409 * theta + 1.656, 2)

        for i in calibrationdistance:
            if R > (i[0] - 1) and R < (i[0] + 1):
                signal[1] = i[1]
                signal[2] = i[2]
                signal[3] = i[3]

        if signal[2] == 0:
            print('i think the cigarette is too far')

        return signal

    def radial(self, x, y):

        # Returns the polar coordinates of the given cartesian coordinates

        R = math.sqrt(x ** 2 + y ** 2)

        theta = math.atan2(x, y)

        return (R, theta)