__author__ = 'mayank'

import numpy as np
import scipy.io as sio
import os

def readPulseOx(filename):
    import pickle
    f = open(filename)
    data = pickle.load(f)
    pulsePPG_tmp = data['pulseOxRecord']
    if isinstance(pulsePPG_tmp[0], tuple):
        pulsePPG = [pulsePPG_tmp[i][0] for i in range(len(pulsePPG_tmp))]
    else:
        pulsePPG = pulsePPG_tmp

    return pulsePPG

def convMat(filename):
    pulsePPG = readPulseOx(filename)

    data={}
    data['pulsePPG'] =pulsePPG
    base = os.path.basename(filename)
    matFilename = os.path.splitext(base)[0]+'.mat'

    sio.savemat(matFilename,data)

def convVideo2PNG(videoFileName):
    #ffmpeg -i 2016-05-25-14-20.mkv  frame_%05d.png
    #ffmpeg -loglevel error -i frame_00000.png -f md5 -
    pass
