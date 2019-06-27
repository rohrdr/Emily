from __future__ import division
import time
import Adafruit_PCA9685
# from __future__ import printfunction
# Initalisierung mit alternativer Adresse
pwm = Adafruit_PCA9685.PCA9685(address=0x41)

# Einstellen der Minimal- und Maximal-Pulslaengen
servo_min = 150  # Minimale Pulslaenge
servo_max = 600  # Maximale Pulslaenge

motorpositions=[0,0,0,0]



def set_servo_pulse(channel, pulse):
    motorpositions[channel]=pulse
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
    pwm.set_pwm(channel, 0, pulse)
    print motorpositions
    
    
def moveslow(channel,pulse):
    
    if (motorpositions[channel]-pulse) > 0 :
        step=-0.01
    else:
        step=0.01
    
    while True:
        if abs(motorpositions[channel]-pulse)<0.0001:
            break
        else:
            set_servo_pulse(channel, motorpositions[channel]+step)
        time.sleep(0.05)
            
    
set_servo_pulse(0,1.6)
time.sleep(0.5)
set_servo_pulse(1,1.48)
time.sleep(0.5)
set_servo_pulse(2,1)
time.sleep(0.5)
set_servo_pulse(3,1)
time.sleep(0.5)
#set_servo_pulse(4,2)
time.sleep(0.5)
#set_servo_pulse(5,1.5)    

    
pwm.set_pwm_freq(50)

while True:
    channel = int(input("Channel [0-5]:"))
    signal = float(input("Signal [0.5-2.5]"))
#    slow = raw_input("slow (Y-N)")
#    print(channel, signal,slow)
    
#    if slow =='Y': 
#    if slow == 'N':
    
    moveslow(channel,signal)
    set_servo_pulse(channel, signal)
        
        
    
