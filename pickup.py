#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car and train a model for it.

Usage:
    python pickup.py

Options:
    -h --help        Show this screen.
    --tub TUBPATHS   List of paths to tubs. Comma separated. Use quotes to use wildcards. ie "~/tubs/*"
"""
import os
import time
from docopt import docopt

import donkeycar as dk
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.actuator import PCA9685, PWMSteering, PWMThrottle
from donkeycar.parts.datastore import TubGroup, TubWriter, TubHandler
#from donkeycar.parts.clock import Timestamp
from donkeycar.parts.network import TCPServeValue
from donkeycar.parts.image import ImgArrToJpg
from Eyes import Eyes
from Brains import Brains
from Emil import Emil
from Runner import Runner


def pickup(cfg):

    """
    Construct a working robotic vehicle from many parts.
    Each part runs as a job in the Vehicle loop, calling either
    it's run or run_threaded method depending on the constructor flag `threaded`.
    All parts are updated one after another at the framerate given in
    cfg.DRIVE_LOOP_HZ assuming each part finishes processing in a timely manner.
    Parts may have named outputs and inputs. The framework handles passing named outputs
    to parts requesting the same named input.
    """

    V = dk.vehicle.Vehicle()

#    clock = Timestamp()
#    V.add(clock, outputs=['timestamp'])

    cam = PiCamera(image_w=cfg.IMAGE_W, image_h=cfg.IMAGE_H, image_d=cfg.IMAGE_DEPTH)
    # for Emily's setup we need to flip the camera and change the shutter speed
    cam.camera.hflip = True
    cam.camera.vflip = True
    cam.camera.shutter_speed = 5000
    V.add(cam, outputs=['image'], threaded=True)

    # get eyes
    model = Eyes(cfg.MODEL_CFG, cfg.MODEL_WEIGHTS, cfg.IMAGE_W, cfg.IMAGE_H)
    V.add(model,
          inputs=['image'],
          outputs=['bboxes'])

    # get strategy
    strategy = Brains(pic_to_reality_csv=cfg.MAP_PATH)
    V.add(strategy,
          inputs=['bboxes'],
          outputs=['angle', 'throttle', 'runtime', 'waittime', 'emily', 'emil', 'x', 'y'])

    # get Emil
    emil = Emil()
    V.add(emil,
          inputs=['x', 'y'],
          run_condition='emil')

    steering_controller = PCA9685(cfg.STEERING_CHANNEL)
    steering = PWMSteering(controller=steering_controller,
                           left_pulse=cfg.STEERING_LEFT_PWM,
                           right_pulse=cfg.STEERING_RIGHT_PWM)

    throttle_controller = PCA9685(cfg.THROTTLE_CHANNEL)
    throttle = PWMThrottle(controller=throttle_controller,
                           max_pulse=cfg.THROTTLE_FORWARD_PWM,
                           zero_pulse=cfg.THROTTLE_STOPPED_PWM,
                           min_pulse=cfg.THROTTLE_REVERSE_PWM)

    V.add(steering, inputs=['angle'], run_condition='emily')
    V.add(throttle, inputs=['throttle'], run_condition='emily')

    # add the stopper
    runner = Runner()
    V.add(runner, inputs=['runtime'], outputs=['throttle2'])

    # add second throttle
    throttle2 = PWMThrottle(controller=throttle_controller,
                           max_pulse=cfg.THROTTLE_FORWARD_PWM,
                           zero_pulse=cfg.THROTTLE_STOPPED_PWM,
                           min_pulse=cfg.THROTTLE_REVERSE_PWM)
    V.add(throttle2, inputs=['throttle2'], run_condition='emily')

    # add the stopper
    runner2 = Runner()
    V.add(runner2, inputs=['waittime'], outputs=['throttle2'])

    if cfg.PUB_CAMERA_IMAGES:
        pub = TCPServeValue("camera")
        V.add(ImgArrToJpg(), inputs=['cam/image_array'], outputs=['jpg/bin'])
        V.add(pub, inputs=['jpg/bin'])

    # add tub to save data
    inputs = ['image', 'angle', 'throttle']
    types = ['image_array', 'float', 'float']

    # multiple tubs
    # th = TubHandler(path=cfg.DATA_PATH)
    # tub = th.new_tub_writer(inputs=inputs, types=types)

    # single tub
    tub = TubWriter(path=cfg.TUB_PATH, inputs=inputs, types=types)
    V.add(tub, inputs=inputs)

    # run the vehicle
    V.start(rate_hz=cfg.DRIVE_LOOP_HZ,
            max_loop_count=cfg.MAX_LOOPS)



if __name__ == '__main__':
    cfg = dk.load_config()
    pickup(cfg)

