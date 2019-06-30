import time

class Emil:

    def __init__(self, controller, rest_position):

        self.rest_position = rest_position
        self.controller = controller
        self.controller.set_pulse(to_pulse(rest_position))
        self.position = rest_position

        return

    def run(self, signal):
        print('in Emil')

        if (self.position - signal) > 0:
            step = -0.01
        else:
            step = 0.01

        loop = True
        while loop:
            if abs(self.position - signal) < 0.0001:
                self.position = signal
                self.controller.set_pulse(to_pulse(self.position))
                time.sleep(2)
                loop = False
            else:
                self.position += step
                self.controller.set_pulse(to_pulse(self.position))
            time.sleep(0.05)

        return


def to_pulse(signal):

        pulse_length = 1000000
        pulse_length /= 50
        #   print('{0}us per period'.format(pulse_length))
        pulse_length /= 4096
        #   print('{0}us per bit'.format(pulse_length))
        pulse = signal * 1000
        #   print(pulse_length)
        pulse /= pulse_length
        #   print(pulse)
        pulse = round(pulse)
        #   print(pulse)
        pulse = int(pulse)
        #   print (pulse)

        return pulse
