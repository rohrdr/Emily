#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import time
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import spidev
import time
import sys
import signal
import logging

# Standardadresse: (0x40).
#pwm = Adafruit_PCA9685.PCA9685()

# Initalisierung mit alternativer Adresse
pwm = Adafruit_PCA9685.PCA9685(address=0x41)

# Einstellen der Minimal- und Maximal-PulslÃ¤ngen
servo_min = 150  # Minimale PulslÃ¤nge
servo_max = 600  # Maximale PulslÃ¤nge

# Hilfsfunktion
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000
    pulse_length /= 50
    pulse_length /= 4096
    pulse *= 1000
    pulse /= pulse_length
    pulse = round(pulse)
    pulse = int(pulse)
    pwm.set_pwm(channel, 0, pulse)

# Frequenz auf 50Hz setzen
pwm.set_pwm_freq(50)

#SPI-Schnittstelle initialisieren für den ADC
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 2000000

Invers = True
NotInvers = False

global Mode1
global modeAuto
global firstmodeAuto

Mode1 = False
modeAuto = False
firstmodeAuto = False


def setLEDBlau():
    # LED Rot
    pwm.set_pwm(9, 0, 0)
    # LED Gruen
    pwm.set_pwm(10, 0, 0)
    # LED Blau
    pwm.set_pwm(11, 0 ,4095)

def setLEDGruen():
    # LED1 Rot
    pwm.set_pwm(9, 0, 0)
    # LED1 Gruen
    pwm.set_pwm(10, 0, 4095)
    # LED1 Blau
    pwm.set_pwm(11, 0 ,0)

def setLEDRot():
    # LED1 Rot
    pwm.set_pwm(9, 0, 4095)
    # LED1 Gruen
    pwm.set_pwm(10, 0, 0)
    # LED1 Blau
    pwm.set_pwm(11, 0 ,0)

setLEDGruen()

GPIO.setmode(GPIO.BCM)

# Hier wird der Eingangs-Pin deklariert, an dem der Sensor angeschlossen ist. Zusaetzlich wird auch der PullUP Widerstand am Eingang aktiviert
BUTTON_PIN = 22
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Diese AusgabeFunktion wird bei Signaldetektion ausgefuehrt
def ausgabeFunktion(null):
    global modeAuto, firstmodeAuto

    modeAuto = not modeAuto

    if modeAuto:
        setLEDRot()
        firstmodeAuto = True
        setStartPosition()
    elif not modeAuto and not Mode1:
        setLEDGruen()
    elif not modeAuto and Mode1:
        setLEDBlau()

# Beim Detektieren eines Signals (fallende Signalflanke) wird die Ausgabefunktion ausgeloest
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=ausgabeFunktion, bouncetime=150)

#Motor Initialisierungswerte
Motor1 = 0
Motor2 = 1
Motor3 = 2
Motor4 = 3
Motor5 = 4
Motor6 = 5

global Motor1StartPosition
global Motor2StartPosition
global Motor3StartPosition
global Motor4StartPosition
global Motor5StartPosition
global Motor6StartPosition

Motor1StartPosition = 1.5
Motor2StartPosition = 1.5
Motor3StartPosition = 1.5
Motor4StartPosition = 1.5
Motor5StartPosition = 1.5
Motor6StartPosition = 1.6

Motor1Minimum = 0.5
Motor2Minimum = 1.1
Motor3Minimum = 0.8
Motor4Minimum = 0.8
Motor5Minimum = 0.5
Motor6Minimum = 1.6

Motor1Maximum = 2.5
Motor2Maximum = 2.2
Motor3Maximum = 1.7
Motor4Maximum = 2.2
Motor5Maximum = 2.5
Motor6Maximum = 2.2

global Motor1Pulse
global Motor2Pulse
global Motor3Pulse
global Motor4Pulse
global Motor5Pulse
global Motor6Pulse

Motor1Pulse = Motor1StartPosition
Motor2Pulse = Motor2StartPosition
Motor3Pulse = Motor3StartPosition
Motor4Pulse = Motor4StartPosition
Motor5Pulse = Motor5StartPosition
Motor6Pulse = Motor6StartPosition

#Initialisierungsfunktion
def setStartPosition():
    global Motor1Pulse
    global Motor2Pulse
    global Motor3Pulse
    global Motor4Pulse
    global Motor5Pulse
    global Motor6Pulse

    set_servo_pulse(Motor1, Motor1StartPosition)
    set_servo_pulse(Motor2, Motor2StartPosition)
    set_servo_pulse(Motor3, Motor3StartPosition)
    set_servo_pulse(Motor4, Motor4StartPosition)
    set_servo_pulse(Motor5, Motor5StartPosition)
    set_servo_pulse(Motor6, Motor6StartPosition)

    Motor1Pulse = Motor1StartPosition
    Motor2Pulse = Motor2StartPosition
    Motor3Pulse = Motor3StartPosition
    Motor4Pulse = Motor4StartPosition
    Motor5Pulse = Motor5StartPosition
    Motor6Pulse = Motor6StartPosition

def readadc(adcnum):
	if adcnum >7 or adcnum <0:
		return-1
	r = spi.xfer2([1,8+adcnum <<4,0])
	adcout = ((r[1] &3) <<8)+r[2]
	return adcout

#Initiale Joystickwerte
Joystick1ObenUnten   = 0
Joystick1LinksRechts = 1
Joystick2ObenUnten   = 2
Joystick2LinksRechts = 3

#Initalisierungsroutine
setStartPosition()

JoystickMaximum = 1023
JoystickMinimum = 500
JoystickParkPosition = 780
JoystickParkPositionMargin = 50

#Geschwindikeitswerte
GeschwindigkeitAuto = 0.008

schnell = 0.5
mittel  = 0.3
langsam = 0.1

GeschwindigkeitAutoFaktor = 0.02
Automargin = 0.103
TaktungAutoModus = 0.008

def MotorBewegung (Motor,MotorPulse,JoystickWert,MotorMinimum,MotorMaximum,Speedfaktor, Invers):
    global Mode1

    if (readadc(Joystick1ObenUnten) == 1023 and readadc(Joystick1LinksRechts) == 1023) and (readadc(Joystick2ObenUnten) == 1023 and readadc(Joystick2LinksRechts) == 1023):
        Mode1 = not Mode1
        time.sleep(.5)
        if Mode1:
            setLEDBlau()
        else:
            setLEDGruen()
        return MotorPulse
    if readadc(JoystickWert) > JoystickParkPosition - 15 and readadc(JoystickWert) < JoystickParkPosition + JoystickParkPositionMargin:
        return MotorPulse
    elif readadc(JoystickWert) > JoystickParkPosition + JoystickParkPositionMargin:
        Geschwindigkeit = (0.005 + (0.015 / 300 * (readadc(JoystickWert) - JoystickParkPosition + JoystickParkPositionMargin))*Speedfaktor)
        if not Invers and not (MotorPulse >= MotorMaximum):
            MotorPulse = MotorPulse + Geschwindigkeit
            set_servo_pulse(Motor, MotorPulse)
        elif Invers and not (MotorPulse < MotorMinimum):
            MotorPulse = MotorPulse - Geschwindigkeit
            set_servo_pulse(Motor, MotorPulse)

    elif readadc(JoystickWert) < JoystickParkPosition - JoystickParkPositionMargin:
        Geschwindigkeit = (0.005 + (0.015 / 400 * ((readadc(JoystickWert) - JoystickParkPosition - JoystickParkPositionMargin) * (-1)))*Speedfaktor)
        if not Invers and not (MotorPulse <= MotorMinimum):
            MotorPulse = MotorPulse - Geschwindigkeit
            set_servo_pulse(Motor, MotorPulse)
        elif Invers and not (MotorPulse >= MotorMaximum):
            MotorPulse = MotorPulse + Geschwindigkeit
            set_servo_pulse(Motor, MotorPulse)
    return MotorPulse

def MotorBewegungAuto (Motor,MotorPulse,MotorMinimum,MotorMaximum,MotorAutoWert,GeschwindigkeitAuto):

    if abs(MotorPulse-MotorAutoWert) <= Automargin:
        MotorPulse = MotorAutoWert
        return MotorPulse

    if MotorPulse < MotorMinimum:
        print 'Motor',Motor
        print 'Minimum Erreicht'
        print MotorPulse
        return MotorPulse

    if MotorPulse > MotorMaximum:
        print 'Motor',Motor
        print 'Maximum Erreicht'
        print  MotorPulse
        return MotorPulse

    if MotorAutoWert < MotorPulse:
        Richtung = True

    elif MotorAutoWert > MotorPulse:
        Richtung = False

    GeschwindigkeitAuto = GeschwindigkeitAuto * GeschwindigkeitAutoFaktor

    if not Richtung and not (MotorPulse >= MotorMaximum):
            MotorPulse = MotorPulse + GeschwindigkeitAuto
            set_servo_pulse(Motor, MotorPulse)
            return MotorPulse

    elif Richtung and not (MotorPulse < MotorMinimum):
            MotorPulse = MotorPulse - GeschwindigkeitAuto
            set_servo_pulse(Motor, MotorPulse)
            return MotorPulse

#Position 1
Motor1AutoPosition1 = 0.9
Motor2AutoPosition1 = 1.8
Motor3AutoPosition1 = 0.9
Motor4AutoPosition1 = 1.8
Motor5AutoPosition1 = 0.9
Motor6AutoPosition1 = 1.8

#Position 2
Motor1AutoPosition2 = 0.9
Motor2AutoPosition2 = 1.5
Motor3AutoPosition2 = 1.2
Motor4AutoPosition2 = 1.2
Motor5AutoPosition2 = 1.9
Motor6AutoPosition2 = 2.2

#Position 3
Motor1AutoPosition3 = 0.9
Motor2AutoPosition3 = 1.8
Motor3AutoPosition3 = 0.9
Motor4AutoPosition3 = 1.8
Motor5AutoPosition3 = 0.9
Motor6AutoPosition3 = 1.8

#Position 4
Motor1AutoPosition4 = 1.9
Motor2AutoPosition4 = 1.8
Motor3AutoPosition4 = 0.9
Motor4AutoPosition4 = 1.8
Motor5AutoPosition4 = 0.9
Motor6AutoPosition4 = 1.6

#Position 5
Motor1AutoPosition5 = 1.3
Motor2AutoPosition5 = 1.2
Motor3AutoPosition5 = 0.9
Motor4AutoPosition5 = 1.8
Motor5AutoPosition5 = 0.9
Motor6AutoPosition5 = 1.8

#Position 6
Motor1AutoPosition6 = 0.9
Motor2AutoPosition6 = 1.8
Motor3AutoPosition6 = 0.9
Motor4AutoPosition6 = 1.8
Motor5AutoPosition6 = 1.9
Motor6AutoPosition6 = 1.6

#Position 7
Motor1AutoPosition7 = 0.5
Motor2AutoPosition7 = 1.7
Motor3AutoPosition7 = 0.9
Motor4AutoPosition7 = 1.8
Motor5AutoPosition7 = 2.2
Motor6AutoPosition7 = 2.2

#Position 8
Motor1AutoPosition8 = 2.2
Motor2AutoPosition8 = 1.4
Motor3AutoPosition8 = 1.2
Motor4AutoPosition8 = 1.8
Motor5AutoPosition8 = 0.9
Motor6AutoPosition8 = 1.8

#Position 9
Motor1AutoPosition9 = 2.0
Motor2AutoPosition9 = 2.2
Motor3AutoPosition9 = 0.9
Motor4AutoPosition9 = 1.2
Motor5AutoPosition9 = 0.9
Motor6AutoPosition9 = 1.8

#Position 10
Motor1AutoPosition10 = 0.9
Motor2AutoPosition10 = 1.8
Motor3AutoPosition10 = 0.9
Motor4AutoPosition10 = 1.8
Motor5AutoPosition10 = 0.9
Motor6AutoPosition10 = 1.8

#Position 11
Motor1AutoPosition11 = 0.9
Motor2AutoPosition11 = 1.8
Motor3AutoPosition11 = 0.9
Motor4AutoPosition11 = 1.8
Motor5AutoPosition11 = 0.9
Motor6AutoPosition11 = 1.8

#Position 12
Motor1AutoPosition12 = 0.9
Motor2AutoPosition12 = 1.8
Motor3AutoPosition12 = 0.9
Motor4AutoPosition12 = 1.8
Motor5AutoPosition12 = 0.9
Motor6AutoPosition12 = 1.8

#Position 13
Motor1AutoPosition13 = 0.9
Motor2AutoPosition13 = 1.8
Motor3AutoPosition13 = 0.9
Motor4AutoPosition13 = 1.8
Motor5AutoPosition13 = 0.9
Motor6AutoPosition13 = 1.8

#Position 14
Motor1AutoPosition14 = 0.9
Motor2AutoPosition14 = 1.8
Motor3AutoPosition14 = 0.9
Motor4AutoPosition14 = 1.8
Motor5AutoPosition14 = 0.9
Motor6AutoPosition14 = 1.8

#Position 15
Motor1AutoPosition15 = 0.9
Motor2AutoPosition15 = 1.8
Motor3AutoPosition15 = 0.9
Motor4AutoPosition15 = 1.8
Motor5AutoPosition15 = 0.9
Motor6AutoPosition15 = 1.8

#Position 15
Motor1AutoPosition16 = 0.9
Motor2AutoPosition16 = 1.8
Motor3AutoPosition16 = 0.9
Motor4AutoPosition16 = 1.8
Motor5AutoPosition16 = 0.9
Motor6AutoPosition16 = 1.8

def AutoModus():
    global Motor1Pulse
    global Motor2Pulse
    global Motor3Pulse
    global Motor4Pulse
    global Motor5Pulse
    global Motor6Pulse
    global firstmodeAuto

    i = 0

    #Position 0
    if firstmodeAuto:
        print 'Start Automodus'
        time.sleep(0.5)
        firstmodeAuto = False
        setStartPosition()


    # Position 1
    if modeAuto:
        i = i+1
        while (      Motor1Pulse != Motor1AutoPosition1
                  or Motor2Pulse != Motor2AutoPosition1
                  or Motor3Pulse != Motor3AutoPosition1
                  or Motor4Pulse != Motor4AutoPosition1
                  or Motor5Pulse != Motor5AutoPosition1
                  or Motor6Pulse != Motor6AutoPosition1

                ):

            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition1, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition1, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition1, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition1, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition1, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition1, mittel)


            time.sleep(TaktungAutoModus)
        print 'Position',i

    # Position 2
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition2
               or Motor2Pulse != Motor2AutoPosition2
               or Motor3Pulse != Motor3AutoPosition2
               or Motor4Pulse != Motor4AutoPosition2
               or Motor5Pulse != Motor5AutoPosition2
               or Motor6Pulse != Motor6AutoPosition2

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition2, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition2, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition2, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition2, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition2, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition2, mittel)

            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 3
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition3
               or Motor2Pulse != Motor2AutoPosition3
               or Motor3Pulse != Motor3AutoPosition3
               or Motor4Pulse != Motor4AutoPosition3
               or Motor5Pulse != Motor5AutoPosition3
               or Motor6Pulse != Motor6AutoPosition3

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition3, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition3, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition3, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition3, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition3, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition3, mittel)

            time.sleep(TaktungAutoModus)
        print 'Position', i


    # Position 4
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition4
               or Motor2Pulse != Motor2AutoPosition4
               or Motor3Pulse != Motor3AutoPosition4
               or Motor4Pulse != Motor4AutoPosition4
               or Motor5Pulse != Motor5AutoPosition4
               or Motor6Pulse != Motor6AutoPosition4

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition4, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition4, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition4, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition4, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition4, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition4, mittel)

            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 5
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition5
               or Motor2Pulse != Motor2AutoPosition5
               or Motor3Pulse != Motor3AutoPosition5
               or Motor4Pulse != Motor4AutoPosition5
               or Motor5Pulse != Motor5AutoPosition5
               or Motor6Pulse != Motor6AutoPosition5

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition5, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition5, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition5, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition5, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition5, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition5, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 6
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition6
               or Motor2Pulse != Motor2AutoPosition6
               or Motor3Pulse != Motor3AutoPosition6
               or Motor4Pulse != Motor4AutoPosition6
               or Motor5Pulse != Motor5AutoPosition6
               or Motor6Pulse != Motor6AutoPosition6

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition6, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition6, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition6, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition6, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition6, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition6, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 7
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition7
               or Motor2Pulse != Motor2AutoPosition7
               or Motor3Pulse != Motor3AutoPosition7
               or Motor4Pulse != Motor4AutoPosition7
               or Motor5Pulse != Motor5AutoPosition7
               or Motor6Pulse != Motor6AutoPosition7

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition7, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition7, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition7, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition7, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition7, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition7, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 8
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition8
               or Motor2Pulse != Motor2AutoPosition8
               or Motor3Pulse != Motor3AutoPosition8
               or Motor4Pulse != Motor4AutoPosition8
               or Motor5Pulse != Motor5AutoPosition8
               or Motor6Pulse != Motor6AutoPosition8

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition8, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition8, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition8, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition8, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition8, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition8, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 9
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition9
               or Motor2Pulse != Motor2AutoPosition9
               or Motor3Pulse != Motor3AutoPosition9
               or Motor4Pulse != Motor4AutoPosition9
               or Motor5Pulse != Motor5AutoPosition9
               or Motor6Pulse != Motor6AutoPosition9

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition9, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition9, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition9, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition9, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition9, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition9, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 10
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition10
               or Motor2Pulse != Motor2AutoPosition10
               or Motor3Pulse != Motor3AutoPosition10
               or Motor4Pulse != Motor4AutoPosition10
               or Motor5Pulse != Motor5AutoPosition10
               or Motor6Pulse != Motor6AutoPosition10

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition10, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition10, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition10, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition10, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition10, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition10, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 11
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition11
               or Motor2Pulse != Motor2AutoPosition11
               or Motor3Pulse != Motor3AutoPosition11
               or Motor4Pulse != Motor4AutoPosition11
               or Motor5Pulse != Motor5AutoPosition11
               or Motor6Pulse != Motor6AutoPosition11

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition11, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition11, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition11, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition11, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition11, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition11, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 12
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition12
               or Motor2Pulse != Motor2AutoPosition12
               or Motor3Pulse != Motor3AutoPosition12
               or Motor4Pulse != Motor4AutoPosition12
               or Motor5Pulse != Motor5AutoPosition12
               or Motor6Pulse != Motor6AutoPosition12

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition12, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition12, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition12, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition12, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition12, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition12, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 13
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition13
               or Motor2Pulse != Motor2AutoPosition13
               or Motor3Pulse != Motor3AutoPosition13
               or Motor4Pulse != Motor4AutoPosition13
               or Motor5Pulse != Motor5AutoPosition13
               or Motor6Pulse != Motor6AutoPosition13

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition13, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition13, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition13, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition13, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition13, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition13, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 14
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition14
               or Motor2Pulse != Motor2AutoPosition14
               or Motor3Pulse != Motor3AutoPosition14
               or Motor4Pulse != Motor4AutoPosition14
               or Motor5Pulse != Motor5AutoPosition14
               or Motor6Pulse != Motor6AutoPosition14

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition14, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition14, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition14, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition14, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition14, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition14, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 15
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition15
               or Motor2Pulse != Motor2AutoPosition15
               or Motor3Pulse != Motor3AutoPosition15
               or Motor4Pulse != Motor4AutoPosition15
               or Motor5Pulse != Motor5AutoPosition15
               or Motor6Pulse != Motor6AutoPosition15

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition15, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition15, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition15, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition15, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition15, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition15, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i

    # Position 16
    if modeAuto:
        i = i + 1
        while (Motor1Pulse != Motor1AutoPosition16
               or Motor2Pulse != Motor2AutoPosition16
               or Motor3Pulse != Motor3AutoPosition16
               or Motor4Pulse != Motor4AutoPosition16
               or Motor5Pulse != Motor5AutoPosition16
               or Motor6Pulse != Motor6AutoPosition16

               ):
            Motor1Pulse = MotorBewegungAuto(Motor1, Motor1Pulse, Motor1Minimum, Motor1Maximum, Motor1AutoPosition16, schnell)
            Motor2Pulse = MotorBewegungAuto(Motor2, Motor2Pulse, Motor2Minimum, Motor2Maximum, Motor2AutoPosition16, mittel)
            Motor3Pulse = MotorBewegungAuto(Motor3, Motor3Pulse, Motor3Minimum, Motor3Maximum, Motor3AutoPosition16, mittel)
            Motor4Pulse = MotorBewegungAuto(Motor4, Motor4Pulse, Motor4Minimum, Motor4Maximum, Motor4AutoPosition16, mittel)
            Motor5Pulse = MotorBewegungAuto(Motor5, Motor5Pulse, Motor5Minimum, Motor5Maximum, Motor5AutoPosition16, mittel)
            Motor6Pulse = MotorBewegungAuto(Motor6, Motor6Pulse, Motor6Minimum, Motor6Maximum, Motor6AutoPosition16, mittel)
            time.sleep(TaktungAutoModus)
        print 'Position', i


    print 'fertig'
    print '--------------'



while True:
   if not Mode1 and not modeAuto:
        Motor1Pulse = MotorBewegung(Motor1, Motor1Pulse, Joystick1LinksRechts,Motor1Minimum,Motor1Maximum,schnell, Invers)
        Motor2Pulse = MotorBewegung(Motor2, Motor2Pulse, Joystick1ObenUnten, Motor2Minimum, Motor2Maximum,schnell, NotInvers)
        Motor3Pulse = MotorBewegung(Motor3, Motor3Pulse, Joystick1ObenUnten, Motor3Minimum, Motor3Maximum, mittel , NotInvers)
        Motor4Pulse = MotorBewegung(Motor4, Motor4Pulse, Joystick2ObenUnten, Motor4Minimum, Motor4Maximum,schnell, Invers)
        Motor5Pulse = MotorBewegung(Motor5, Motor5Pulse, Joystick2LinksRechts, Motor5Minimum, Motor5Maximum,schnell, NotInvers)
   elif Mode1 and not modeAuto:
        Motor6Pulse = MotorBewegung(Motor6, Motor6Pulse, Joystick1ObenUnten, Motor6Minimum, Motor6Maximum, schnell, Invers)
        Motor6Pulse = MotorBewegung(Motor6, Motor6Pulse, Joystick2ObenUnten, Motor6Minimum, Motor6Maximum, schnell , Invers)
    
   while modeAuto:
    	AutoModus()
    	time.sleep(0.01)

   time.sleep(0.01)








