from multiprocessing import  Process, get_logger
from queue import Empty
import logging
from time import sleep
import datetime
import os

# Scientific computing 
import numpy as np
from scipy import io
import cv2
import pickle

import shutil
import json

from IPython import embed

class storage_PulseOx(Process):
    def __init__(self, pulseOxBuffer, stopStorage, basePath, pxID):
        Process.__init__(self)
        self.pulseOxBuffer = pulseOxBuffer
        if self.pulseOxBuffer is None:
            self.pulseOx = False
        else:
            self.pulseOx = True 

        self.stopStorage = stopStorage
        self.basePath = basePath
        self.pxID = pxID


        self.pulseOxCounter = 0
        # self.fourcc = cv2.cv.FOURCC('L','A','G','S')
        # NOTE: ffmpeg do not support LAGS encoding and so this does not work

        #self.pulseSizeFactor=1


    def run(self):

        pulseOxRecord = []
        pulseOxTimeRecord = []
        while not self.stopStorage.is_set():
            if self.pulseOx:
                while not self.pulseOxBuffer.empty():
                    try:
                        (pulseOxTime,pulsePPG) = self.pulseOxBuffer.get(block=False)
                    except Empty:
                        continue
                    self.pulseOxCounter+=1
                    pulseOxRecord.append(pulsePPG)
                    pulseOxTimeRecord.append(pulseOxTime)

            # pickle the rest of the data
            data = {}
            data['pulseOxRecord'] = np.array(pulseOxRecord).reshape((-1,))
            data['pulseOxTime'] = np.array(pulseOxTimeRecord).reshape((-1,))

            data['numPulseSample'] = self.pulseOxCounter
            # dirty way, but simple to implement
            f = open(os.path.join(self.basePath, self.pxID+'_partial.pkl'),'w') # 'w' will overwrite everytime
            pickle.dump(data, f)
            f.close()

            # Write in a text file
            thefile = open(os.path.join(self.basePath,self.pxID+'_partial_log.txt'),'w')
            json.dump(data['pulseOxTime'].tolist(),thefile)
            thefile.close()

            # write a .mat file
            with open(os.path.join(self.basePath,self.pxID+'_partial.mat'),'w') as f:
                io.savemat(f,data)



        # final storage
        if self.pulseOx:
            while not self.pulseOxBuffer.empty():
                try:
                    (pulseOxTime,pulsePPG) = self.pulseOxBuffer.get(block=False)
                except Empty:
                    continue
                # logger.debug('pulseOxCounter = ' + str(self.pulseOxCounter))
                self.pulseOxCounter+=1
                pulseOxRecord.append(pulsePPG)
                pulseOxTimeRecord.append(pulseOxTime)

        # picle the rest of the data

        data = {}
        data['pulseOxRecord'] = np.array(pulseOxRecord).reshape((-1,))
        data['pulseOxTime'] = np.array(pulseOxTimeRecord).reshape((-1,))
        data['numPulseSample'] = self.pulseOxCounter



        f = open(os.path.join(self.basePath,self.pxID+'_full.pkl'),'w') # 'w' will overwrite everytime
        # 'w' will overwrite everytime
        pickle.dump(data, f)
        f.close()

        # write in a .txt file
        thefile = open(os.path.join(self.basePath,self.pxID+'_full_log.txt'),'w')
        json.dump(data['pulseOxTime'].tolist(),thefile)
        thefile.close()

        # write a .mat file
        with open(os.path.join(self.basePath, self.pxID + '_full.mat'), 'w') as f:
            io.savemat(f, data)








