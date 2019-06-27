from __future__ import division
import time
import Adafruit_PCA9685
import math
import argparse
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
            
def radial(x,y):
    
    #Returns the polar coordinates of the given cartesian coordinates
    
    R=math.sqrt(x**2+y**2)
    
    theta=math.atan2(x,y)
    
    return(R,theta)

def motors(x,y):
    
    signal=[0,0,0,0]
    
    calibrationdistance=[(32,1.48,1,1.05),
                         (30,1.4,1,1),
                         (28,1.3,0.9,1),
                         (26,1.28,0.73,1),
                         (24,1.2,0.63,1),
                         (22,1.12,0.52,1),
                         (20,1.08,0.48,1),
                         (18,1,0.4,0.95),
                         (16,0.95,0.4,0.86),
                         (14,0.92,0.4,0.71),
                         (12,0.9,0.4,0.71),
                         (10,0.88,0.4,0.66),
                        ]  
    
    
    R,theta=radial(x,y)
    
    signal[0]=round(-0.5409*theta+1.656,2)
    
    for i in calibrationdistance:
        if R>(i[0]-1) and R<(i[0]+1):
            signal[1]=i[1]
            signal[2]=i[2]
            signal[3]=i[3]
            
    if signal[2]==0:
        print'i think the cigarette is too far'
    
    
    
    
    return signal


    
set_servo_pulse(0,1.6)
time.sleep(0.5)
set_servo_pulse(1,0.8)
time.sleep(0.5)
set_servo_pulse(2,1)
time.sleep(0.5)
set_servo_pulse(3,1)
time.sleep(0.5)
#set_servo_pulse(4,2)
time.sleep(0.5)
#set_servo_pulse(5,1.5)    

    
pwm.set_pwm_freq(50)

reset=[1.6,0.8,1,1]



while True:
    x = float(input("x coordinate:"))
    y = float(input("y coordinate"))
#    slow = raw_input("slow (Y-N)")
#    print(channel, signal,slow)
    
#    if slow =='Y': 
#    if slow == 'N':
    R,theta=radial(x,y)
    
    if R>30:
        print "cigarette out of reach"
        
    else:

        positions=motors(x,y)
        print R
        print theta
        print positions
        
        for i in range(len(positions)):
            moveslow(i,positions[i])
            set_servo_pulse(i,positions[i])
            time.sleep(0.5)
        
        time.sleep(1)
        
        for i in range(len(reset)):
            moveslow(i,reset[i])
            set_servo_pulse(i,reset[i])
            time.sleep(0.5)
    

        