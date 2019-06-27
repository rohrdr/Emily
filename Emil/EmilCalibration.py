#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 16:29:34 2019

@author: henri
"""

import math
import argparse



def radial(x,y):
    
    #Returns the polar coordinates of the given cartesian coordinates
    
    R=math.sqrt(x**2+y**2)
    
    theta=math.atan2(x,y)
    
    return(R,theta)
    

#x=np.array([0,1,1,1,1,2,1,2,-1,-1,-1,-1,-2,-1,-2])
#y=np.array([0,9,6,4,3,5,2,3,9,6,4,3,5,2,3])
#calibration=np.array([1.65,1.6,1.57,1.53,1.48,1.45,1.41,1.33,1.71,1.75,1.79,1.82,1.87,1.91,1.97])
#
#angle=np.array([math.atan2(i,j) for i,j in zip(x,y)])
#
#
#plt.scatter(angle, calibration)
#plt.show()
#
#regr = linear_model.LinearRegression()
#regr.fit(angle.reshape(-1,1), calibration)
#
#
#
#y_pred = regr.predict(angle.reshape(-1,1))
#
#plt.plot(angle, y_pred, color='blue', linewidth=3)
#
#print('Coefficients: \n', regr.coef_)
#
#coefficients=[regr.coef_[0],regr.intercept_]


def motors(x,y):
    
    signal=[0,0,0,0]
    
    calibrationdistance=[(32,1.48,1,1.05),
                         (30,1.4,1,1),
                         (28,1.3,0.9,1),
                         (26,1,28,0,73,1),
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
    print('R: ',R,' theta: ',theta*360/(2*(math.pi)))
    
    signal[0]=-0.5409*theta+1.656
    
    for i in calibrationdistance:
        if R>(i[0]-1) and R<(i[0]+1):
            signal[1]=i[1]
            signal[2]=i[2]
            signal[3]=i[3]
            
    if signal[2]==0:
        print('i think the cigarette is too far')
    
    
    
    print(signal)
    
    return signal


