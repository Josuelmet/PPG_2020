from multiprocessing import  Process, get_logger
from queue import Empty
import logging
from time import sleep
import datetime
import os

# Scientific computing 
import numpy as np
from scipy import interpolate
import cv2
import pickle
import json

import shutil

from IPython import embed

class storage(Process):
    def __init__(self, frameBuffer, stopStorage, basePath, camID):
        Process.__init__(self)
        self.frameBuffer = frameBuffer

        self.stopStorage = stopStorage
        self.basePath = basePath
        self.camID = camID




        self.frameCounter = 0
        self.storeVideo = False
        # self.fourcc = cv2.cv.FOURCC('L','A','G','S')
        # NOTE: ffmpeg do not support LAGS encoding and so this does not work


        #self.frameSizeFactor = 1
        #self.pulseSizeFactor=1


    def run(self):
        imageFolder = os.path.join(self.basePath,self.camID)
        # make folders
        if not os.path.exists(imageFolder):
            os.makedirs(imageFolder)


        logger = get_logger()
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(processName)s - %(levelname)s - %(message)s')


        # logging to file
        fh = logging.FileHandler(os.path.join(self.basePath, self.camID+'_debug.log'))

        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        # logging to console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)



        logger.addHandler(console)
        logger.addHandler(fh)


        logger.setLevel(logging.DEBUG)
        self.logger = logger

        #videoHandle = cv2.VideoWriter(systemTime+'.avi',self.fourcc,30.0, (640,480))


        logger.info('storing camera and pulse ox Frames ... ')
        cameraTimeRecord = []
        #pulseOxRecord = []
        #pulseOxTimeRecord = []

        # store the camera frames
        while not self.frameBuffer.empty() or not self.stopStorage.is_set():
            try:
                (currentTime,frame)=self.frameBuffer.get(block=False)
            except Empty:
                continue

            # check if color or B/W
            if frame.ndim ==3:
                #frame_perfusion = frame[:,:,1]
                frame_perfusion = frame
                COLOR_FLAG = True
            elif frame.ndim==2:
                frame_perfusion = frame
                COLOR_FLAG = False
            else:
                logger.warn('Wrong frame format, 2D (mono) or 3D (color) numpy array accepted')

            frameFile = os.path.join(imageFolder,'frame_{0:05d}.png'.format(self.frameCounter))

            cv2.imwrite(frameFile, frame_perfusion)
            # videoHandle.write(frame_perfusion)

            self.frameCounter+=1
            cameraTimeRecord.append(currentTime)

            # store data in between

            if self.frameCounter % 300 == 0: # every 10 sec approximately
                logger.info('stored {0} frames in {1:.2f} sec time, frames left in buffer = {2}'.format(str(self.frameCounter), cameraTimeRecord[-1] - cameraTimeRecord[0], str(self.frameBuffer.qsize()) ))


                with open("WCBuffer.txt", "a") as myfile:
                    myfile.write(str(self.frameBuffer.qsize()))




                # picle the rest of the data
                data = {}
                data['cameraTime'] = np.array(cameraTimeRecord).reshape((-1,))

                data['numFrames'] = self.frameCounter

                data['imageWidth'] = frame_perfusion.shape[0]
                data['imageHeight'] = frame_perfusion.shape[1]


                # dirty way, but simple to implement
                f = open(os.path.join(self.basePath,self.camID+'_partial.pkl'),'w') # 'w' will overwrite everytime
                pickle.dump(data, f)
                f.close()



                thefile = open(os.path.join(self.basePath,self.camID+'_wc_partial_log.txt'),'w')
                json.dump(data['cameraTime'].tolist(),thefile)
                thefile.close()


                #logger.debug('Successfully stored {0} frames, and {1} pulse-Ox samples'.format(self.frameCounter,self.pulseOxCounter))


        #videoHandle.release()

        # final storage
        logger.info('Successfully stored {0} frames, now storing camera timing data'.format(self.frameCounter))


        # picle the rest of the data

        data = {}
        data['cameraTime'] = np.array(cameraTimeRecord).reshape((-1,))

        data['numFrames'] = self.frameCounter
        data['imageWidth'] = frame_perfusion.shape[0]
        data['imageHeight'] = frame_perfusion.shape[1]


        f = open(os.path.join(self.basePath,self.camID+'_full.pkl'),'w') # 'w' will overwrite everytime
         # 'w' will overwrite everytime
        pickle.dump(data, f)
        f.close()


        thefile = open(os.path.join(self.basePath,self.camID+'_wc_full_log.txt'),'w')
        json.dump(data['cameraTime'].tolist(),thefile)
        thefile.close()



        logger.info('Done saving data ... quitting ')



        # Store frames as a loss-less compression
        if self.storeVideo:
            # FIXME: This code uses ffmpeg to convert PNG to Video losslessly, but I found the checksum
            # FIXME: between original and converted image to not be same. Maybe there are issues related to
            # FIXME: color-space conversion, e.g. see http://stackoverflow.com/questions/6701805/h264-lossless-coding

            os.chdir(imageFolder)

            logger.info('Compressing saved images losslessly ... Please wait ')
            FFMPEG_input = 'frame_%05d.png'
            FFMPEG_output = self.camID + '.mkv'
            FFMPEG_FPS = 30

            FFMPEG_command = 'ffmpeg -i '+ FFMPEG_input +' -c:v libx264 -preset veryslow -qp 0 ' + FFMPEG_output
            logger.info(FFMPEG_command)

            os.system(FFMPEG_command)

            ## Remove PNG files
            logger.info('Removing temporary PNG files ... ')

            shutil.move(FFMPEG_output,'..')
            os.chdir('..')
            shutil.rmtree(imageFolder)














