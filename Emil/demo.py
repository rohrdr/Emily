from __future__ import division
import time
import Adafruit_PCA9685
# from __future__ import printfunction
# Initalisierung mit alternativer Adresse
pwm = Adafruit_PCA9685.PCA9685(address=0x41)

# Einstellen der Minimal- und Maximal-Pulslaengen
servo_min = 150  # Minimale Pulslaenge
servo_max = 600  # Maximale Pulslaenge




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
    
pwm.set_pwm_freq(50)

set_servo_pulse(0,2)
time.sleep(0.5)
set_servo_pulse(1,0.8)
time.sleep(0.5)
set_servo_pulse(2,1)
time.sleep(0.5)
set_servo_pulse(3,0.4)
time.sleep(0.5)
set_servo_pulse(4,0.4)
time.sleep(0.5)
set_servo_pulse(5,2)
time.sleep(0.5)


for signal in [1,2,1,2]:
    
    set_servo_pulse(0,signal)
    time.sleep(1)
    
for signal in [1,0.9,1,0.9]:
    
    set_servo_pulse(1,signal)
    time.sleep(1)
    
for signal in [0.4,1,0.4,1]:
    
    set_servo_pulse(2,signal)
    time.sleep(1)

for signal in [1.2,0.4,1.2,0.4]:
    
    set_servo_pulse(3,signal)
    time.sleep(1)
    
    
    
for signal in [1,0.4,1,0.4]:
    
    set_servo_pulse(4,signal)
    time.sleep(1)

for signal in [1.5,2,1.5,2]:
    
    set_servo_pulse(5,signal)
    time.sleep(1)
    

    

    
    