import picamera
import numpy as np
from picamera.array import PiRGBAnalysis
from picamera.color import Color

import matplotlib.pyplot as plt

from datetime import datetime

## Heartrate analysis package
import heartpy as hp
from heartpy.exceptions import BadSignalWarning

# Allows for filtering
import scipy.signal
import scipy.fftpack


# For pulse oximeter
from pulseoximeter import CMS50D

# For camera lights
import RPi.GPIO as gpio

from performancetracker import PerformanceTracker
from ppg_v4_qt import PPG_GUI
from ppg_v4_writer import PPG_Writer



'''
    * The following does not account for Writing time, which does consume a couple FPS. *
    
    Performance Observations at full resolution:
    Analysis + GUI --> ~15 FPS
    Only GUI --> ~25 FPS
    Only Analysis --> ~20 FPS
    None --> 30+ FPS
    
    Performance Observations at smaller resolution:
    Analysis + GUI --> ~15 FPS
    Only GUI --> 30+ FPS
    Only Analysis --> ~30 FPS
'''


'''
    TODO:
    - figure out how to make the PPG actually work... ambient light?
'''





USE_GUI = False
USE_RT_ANALYSIS = False
LIGHT_COLOR = 'WHITE'


RED_PIN = 12
BLUE_PIN = 16
WHITE_PIN = 21




# Initalize data arrays
camData    = np.zeros(50)
camBPMData = np.zeros(50)
psData     = np.zeros(50)
psBPMData  = np.zeros(50)

# Initialize time array
# Used linspace instead of arange due to spacing errors
time = np.linspace(start=0,stop=5.0,num=50)



# Initialize GUI
data_dict = {'time':time,
             'camData':camData, 'camBPMData':camBPMData,
             'psData':psData, 'psBPMData':psBPMData}

if (USE_GUI):
    ppg_gui = PPG_GUI(data_dict)


writer = PPG_Writer()

tracker = PerformanceTracker()



class MyColorAnalyzer(PiRGBAnalysis):
    def __init__(self, _camera):
        super(MyColorAnalyzer, self).__init__(_camera)

        #self.row=209
        self.row=190
        #self.column=145
        self.column=300
        self.window=20
        
        # Miscellaneous variables
        self.last_color = ''
        self.START_TIME = datetime.now()
      
      

      

    def analyze(self, a):
        
        # Correct the orientation of the frame.
        frame = np.fliplr( np.rot90(a) )
        
        print('frame.shape = {}'.format(frame.shape))
        
        global camData, camBPMData, psData, psBPMData, time
        
        signal_window = frame[self.row:self.row+self.window, self.column:self.column+self.window, :]
        
        if (LIGHT_COLOR == 'RED'):
            signal_window = signal_window[:, :, 0]
        elif (LIGHT_COLOR == 'BLUE'):
            signal_window = signal_window[:, :, 1]
        
        signal = np.mean(np.mean(signal_window))

        
        # shift data in the arrays one sample left
        camData[:-1]    = camData[1:]  
        camBPMData[:-1] = camBPMData[1:]
        psData[:-1]     = psData[1:] 
        psBPMData[:-1]  = psBPMData[1:]
        time[:-1]       = time[1:]
        
        
        camData[-1] = signal
        
        time[-1] = (datetime.now() - self.START_TIME).total_seconds()
        
        fps = 1/ (time[1]-time[0])
        
    
    
        cam_bpm = 0    
        
        if (fps < 0):
            print('negative fps: {}'.format(fps))
            
        elif USE_RT_ANALYSIS:
            camSig = camData - np.mean(camData)
            filtered_ppg_r = hp.filter_signal(camSig, 
                                    cutoff = [0.8, 1], 
                                    filtertype = 'bandpass',
                                    sample_rate = fps, 
                                    order = 4,
                                    return_top = False)
            try:
                working_data, measures = hp.process(camSig, 10.0)
            except BadSignalWarning:
                print("Bad signal")
            else:
                if(measures['bpm'] > 50 and measures['bpm'] < 120):
                    cam_bpm = measures['bpm']
                   
        
                    
        
        data = pulseOx.get_data()
        
        psData[-1] = data['pulseWaveform']
        psBPMData[-1] = data['pulseRate']  
        camBPMData[-1] = cam_bpm
        
        
        if (USE_GUI):
            ppg_gui.update(self.draw_window(frame), data_dict)
        
        writer.save_to_csv(data_dict)
        
        tracker.track_performance(False, True)
        print('(cam_bpm={} , fps={})'.format(int(cam_bpm), int(fps)))

    


    
    def draw_window(self, a):
        row1 = self.row
        row2 = self.row + self.window
        col1 = self.column
        col2 = self.column + self.window
        
        frame = np.copy(a)
        print(frame.shape)
        for color_index in range(3):
            for row in range(row1, row2):
                frame[row, col1-3, color_index] = 255
                frame[row, col1-2, color_index] = 255
                frame[row, col1-1, color_index] = 255
                frame[row, col1, color_index] = 255
                frame[row, col2, color_index] = 255
                frame[row, col2+1, color_index] = 255
                frame[row, col2+2, color_index] = 255
                frame[row, col2+3, color_index] = 255
                
            for col in range(col1, col2):
                frame[row1-3, col, color_index] = 255
                frame[row1-2, col, color_index] = 255
                frame[row1-1, col, color_index] = 255
                frame[row1, col, color_index] = 255
                frame[row2, col, color_index] = 255
                frame[row2+1, col, color_index] = 255
                frame[row2+2, col, color_index] = 255
                frame[row2+3, col, color_index] = 255
            
        return frame
    





pulseOx=CMS50D("/dev/ttyUSB0")

## Lights setup
gpio.setmode(gpio.BCM)

pin = 0
if (LIGHT_COLOR == 'RED'):
    pin = RED_PIN
elif (LIGHT_COLOR == 'BLUE'):
    pin = BLUE_PIN
elif (LIGHT_COLOR == 'WHITE'):
    pin = WHITE_PIN

gpio.setup(pin, gpio.OUT)
gpio.output(pin, gpio.HIGH)


#with picamera.PiCamera(resolution='640x480') as camera:
with picamera.PiCamera() as camera:
    
    # Fix the camera's white-balance gains
    camera.awb_mode = 'off'
    camera.awb_gains = (1.4, 1.5)


    # Construct the analysis output and start recording data to it
    with MyColorAnalyzer(camera) as analyzer:
        
        camera.start_recording(analyzer, 'rgb')
        tracker.reset()
        if (USE_GUI):
            ppg_gui.start()
        
        try:
            #while (True):    
            camera.wait_recording(10)
                
        finally:
            camera.stop_recording()
            
            


''' Post-recording code '''
for i in range(5):
    print('stopped recording..')
pulseOx.close()
gpio.cleanup()



# Ignore the first second of data, since it's very different from the other data.
new_time_data = writer.get_time_data()[30:]
new_cam_data = writer.get_cam_data()[30:]

    
# Display the raw PPG data
plt.plot(new_time_data, new_cam_data)
plt.ylabel('recorded cam data')
plt.xlabel('recorded times')
plt.show()


# Display the filtered PPG, print the heartpy bpm estimate    
filtered_ppg, bpm_estimate = writer.get_bpm_estimate(new_time_data, new_cam_data)
print('bpm = {}'.format(bpm_estimate))
plt.plot(new_time_data, filtered_ppg)
plt.ylabel('filtered PPG')
plt.show()



N = len(new_cam_data)
fs = writer.get_samplerate()

# Take FFT of the filtered pp.
# Develop the frequency axis on which to graph the FFT.
ppg_spectrum = scipy.fftpack.fft(filtered_ppg)
ppg_spectrum = np.abs( ppg_spectrum[:N//8] )
frequency_axis = np.linspace(0, fs//8, N//8)


# Graph the FFT.
fig, ax = plt.subplots()
ax.plot(frequency_axis, ppg_spectrum)
plt.show()

# Get the index of the largest value of the spectrum.
peak_frequency_index = np.argmax(ppg_spectrum)
print('my bpm estimate: {}'.format(frequency_axis[peak_frequency_index] * 60.0)) 

print('done')

