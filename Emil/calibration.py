from __future__ import division
import time
import Adafruit_PCA9685
# from __future__ import printfunction
# Initalisierung mit alternativer Adresse
pwm = Adafruit_PCA9685.PCA9685(address=0x41)

# Einstellen der Minimal- und Maximal-Pulslaengen
servo_min = 150  # Minimale Pulslaenge
servo_max = 600  # Maximale Pulslaenge

# Hilfsfunktion
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000
    pulse_length /= 50
    print('{0}us per period'.format(pulse_length))
    pulse_length /= 4096
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    print(pulse_length)
    pulse /= pulse_length
    print(pulse)
    pulse = round(pulse)
    print(pulse)
    pulse = int(pulse)
    print (pulse)
    pwm.set_pwm(channel, 0, pulse)

# Frequenz auf 50Hz setzen
pwm.set_pwm_freq(50)

# Bewege Servo 0-4 auf Position 1500
# Bewege Servo 5 auf Position 1600
set_servo_pulse(0,1.5)
time.sleep(1.5)
#set_servo_pulse(1,1.5)
#time.sleep(1.5)
set_servo_pulse(2,1.5)
time.sleep(1.5)
set_servo_pulse(3,1.5)
time.sleep(1.5)
set_servo_pulse(4,1.5)
time.sleep(1.5)
set_servo_pulse(5,1.5)
time.sleep(1.5)
