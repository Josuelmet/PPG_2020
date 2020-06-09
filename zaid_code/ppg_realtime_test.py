import picamera
import numpy as np
from picamera.array import PiRGBAnalysis
from picamera.color import Color

# GUI and plotting tools
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from scipy import fftpack
import pyqtgraph.console

import sys
import serial
import array

import os
import re
from PyQt4 import Qt, QtGui, QtCore
#import PyQt4.Qwt5 as Qwt
from datetime import datetime

## Heartrate analysis package
import heartpy as hp
from heartpy.exceptions import BadSignalWarning

# Allows for filtering
from scipy import signal
from scipy.signal import butter, lfilter

# For file saving
import time
import array
from datetime import datetime
import csv
import io

## Qt GUI Setup
pg.mkQApp()
win = pg.GraphicsLayoutWidget()
camPen = pg.mkPen(width=10, color='y')
psPen = pg.mkPen(width=10,color='g')
win.setWindowTitle('Remote PPG')
# end Qt Setup

#### GUI Setup
## Plot for image
imgPlot = win.addPlot(colspan=2)
imgPlot.getViewBox().setAspectLocked(True)
win.nextRow()

## Plot for camera intensity
camPlot = win.addPlot()
camBPMPlot = win.addPlot()
win.nextRow()

## Plot for pulse sensor intensity
psPlot = win.addPlot()
psBPMPlot = win.addPlot()

# ImageItem box for displaying image data
img = pg.ImageItem()
imgPlot.addItem(img)
imgPlot.getAxis('bottom').setStyle(showValues=False)
imgPlot.getAxis('left').setStyle(showValues=False)
imgPlot.getAxis('bottom').setPen(0,0,0)
imgPlot.getAxis('left').setPen(0,0,0)
#
#app = QtWidgets.QApplication(sys.argv)
#w = MainWindow()
win.show()
#QtGui.QApplication.instance().exec_()
# Display the window
#### end GUI Setup

fs = 100
start_time = datetime.now()
ptr=0
# Initalize
camData = np.random.normal(size=50)
camBPMData = np.zeros(50)

psData = np.random.normal(size=50)
psBPMData = np.zeros(50)

###Setting axis label

camPlot.getAxis('bottom').setStyle(showValues=False)
camPlot.getAxis('left').setStyle(showValues=False)

camBPMPlot.getAxis('bottom').setStyle(showValues=False)
camBPMPlot.setLabel('left','PulseOx SpO2')

# Used linspace instead of arange due to spacing errors
t = np.linspace(start=0,stop=5.0,num=50)
psTime = np.linspace(start=0,stop=5.0,num=50)

camCurve = camPlot.plot(t, camData, pen=camPen,name="Camera")
camPlot.setLabel('left','Cam Signal')

camBPMCurve = camBPMPlot.plot(t,camBPMData,pen=camPen,name="Cam BPM")

psCurve = psPlot.plot(t, psData, pen=psPen,name="Pulse Sensor")

psBPMCurve = psBPMPlot.plot(t, psBPMData, pen=psPen,name="PS BPM")

psPlot.getAxis('bottom').setStyle(showValues=False)
psPlot.getAxis('left').setStyle(showValues=False)
psPlot.setLabel('left','PS Signal')


#imgPlot.addItem(box)


class CMS50D(object):
    #TODO: Properly decode "finger out" flag, assuming it exists
    def __init__(self, portstr):
        self.port = serial.Serial(portstr, 19200, timeout=0.1, stopbits=1, parity=serial.PARITY_ODD, bytesize=8)
        self.current_bpm = None
        self.current_spo2 = None
        self._buf = array.array('B')
    def get_data(self):
        self._buf.frombytes(self.port.read(8))
#        print(self.port.read(8))
        
        data = []
        i = 0
        state = 0
        lvl = 0
        pulse = 0
        blip = 0
        ox = 0
        while (len(self._buf) >= (5 - state)):
            b = self._buf.pop(0)
            if state == 0:
                if b & 0x80 == 0x80:
                    if (b & 0x40):
                        blip = 1
                    else:
                        blip = 0
                    state = 1
            elif state == 1:
                lvl = b
                state = 2
            elif state == 2:
                if (b & 0x40):
                    pulse = 128
                else:
                    pulse = 0
                state = 3
            elif state == 3:
                pulse += b
                state = 4
            elif state == 4:
                ox = b
                data.append((lvl,blip,pulse,ox))
                state = 0
        return data
    def close(self):
        self.port.close()
        


class MyColorAnalyzer(PiRGBAnalysis):
    def __init__(self, camera):
        super(MyColorAnalyzer, self).__init__(camera)
#        self.last_color = ''
        self.row=209
        self.column=145
        self.window=20
        win.show()
#        

    def analyze(self, a):
        # Convert the average color of the pixels in the middle box
#        c = Color(
#            r=int(np.mean(a[30:60, 60:120, 0])),
#            g=int(np.mean(a[30:60, 60:120, 1])),
#            b=int(np.mean(a[30:60, 60:120, 2]))
#            )
        
        signal=np.mean(np.mean(a[self.row:self.row+self.window, self.column:self.column+self.window, 0]))
#        print(signal)

#        image = image.T
        img.setImage(a, autoLevels=True)
        
        camData[:-1] = camData[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
        camData[-1] = signal
        t[:-1] = t[1:]
        t[-1] = (datetime.now() - start_time).total_seconds()
        fps=1/(t[1]-t[0])
        print(1/(t[1]-t[0]))
#        print(a.shape)

#        cam_bpm = camBPMData[-1]
#        camSig = camData - np.mean(camData)
#        filtered_ppg_r = hp.filter_signal(camSig, 
#                                cutoff = [0.8, 1], 
#                                filtertype = 'bandpass',
#                                sample_rate = fps, 
#                                order = 4,
#                                return_top = False)
#        try:
#            working_data, measures = hp.process(camSig, 10.0)
#        except BadSignalWarning:
#            print("Bad signal")
#        else:
#            if(measures['bpm'] > 50 and measures['bpm'] < 120):
#                cam_bpm = measures['bpm']
    ### end HeartPy

##       Processing signal
#        filtered_ppg_r = hp.filter_signal(signal, 
#                                cutoff = [0.8, 3], 
#                                filtertype = 'bandpass',
#                                sample_rate = fps, 
#                                order = 4,
#                                return_top = False)
#        
        data=pulseOx.get_data()
        psData[:-1] = psData[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
        psData[-1] = data[0][0]

        psBPMData[:-1] = psBPMData[1:]
        psBPMData[-1] = data[0][2]
        #Pulse oximetry
        camBPMData[:-1] = camBPMData[1:]
        camBPMData[-1] = data[0][3]

#        camBPMData[:-1] = camBPMData[1:]
#        camBPMData[:-1] = cam_bpm
#        ptr += 1
        camCurve.setData(camData)
#        camCurve.setPos(ptr, 0)

        psCurve.setData(psData)
        psBPMCurve.setData(psBPMData)
        camBPMCurve.setData(camBPMData)

    


        # Convert the color to hue, saturation, lightness
#        h, l, s = c.hls
#        c = 'none'
#        if s > 1/3:
#            if h > 8/9 or h < 1/36:
#                c = 'red'
#            elif 5/9 < h < 2/3:
#                c = 'blue'
#            elif 5/36 < h < 4/9:
#                c = 'green'
#        # If the color has changed, update the display
#        if c != self.last_color:
#            self.camera.annotate_text = c
##            self.last_color = c
#if __name__ == '__main__':
#    import sys
#    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        QtGui.QApplication.instance().exec_()

pulseOx=CMS50D("/dev/ttyUSB0")

with picamera.PiCamera(resolution='640x480') as camera:
    # Fix the camera's white-balance gains
    camera.awb_mode = 'off'
    camera.awb_gains = (1.4, 1.5)
    # Draw a box over the area we're going to watch 
#    camera.start_preview(alpha=128)
#    box = np.zeros((96, 160, 3), dtype=np.uint8)
#    box[30:60, 60:120, :] = 0x80
#    camera.add_overlay(memoryview(box), size=(160, 90), layer=3, alpha=64)
    # Construct the analysis output and start recording data to it
    with MyColorAnalyzer(camera) as analyzer:
        camera.start_recording(analyzer, 'rgb')
        QtGui.QApplication.instance().exec_()
        try:
            while True:
                camera.wait_recording(1)
        finally:
            camera.stop_recording()
            pulseOx.close()
            

