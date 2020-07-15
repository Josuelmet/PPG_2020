import picamera
import numpy as np
from picamera.array import PiRGBAnalysis

import matplotlib.pyplot as plt

from datetime import datetime

## Heartrate analysis package
import heartpy as hp
from heartpy.exceptions import BadSignalWarning


# For pulse oximeter
from pulseoximeter import CMS50D

# For camera lights
import RPi.GPIO as gpio

from performancetracker import PerformanceTracker
from ppg_v7_writer import PPG_Writer
import ppg_v7_analysis as ppg_analysis





LOWER_RES = False
RECORD_CAMERA = False
LIGHT_COLOR = 'WHITE'


RED_PIN = 12
WHITE_PIN = 21




class DummyAnalyzer(PiRGBAnalysis):
    def __init__(self, _camera):
        super(DummyAnalyzer, self).__init__(_camera)
        self.analyze_count = 0
        
    def analyze(self, a):
        self.analyze_count = self.analyze_count + 1
        print('dummy call #{}'.format(self.analyze_count))
        
        print(a.shape)




class MyColorAnalyzer(PiRGBAnalysis):
    def __init__(self, _camera):
        super(MyColorAnalyzer, self).__init__(_camera)

        if LOWER_RES:
            self.row    = 50
            self.column = 150
            self.window = 250
        else:
            self.row    = 150
            self.column = 300
            self.window = 400
        
        # Miscellaneous variables
        self.START_TIME = datetime.now()
      
      

      

    def analyze(self, a):
        global camDataRed, camDataGreen, camBPMData, psData, psBPMData, time, camera        

        
        red_window = a[self.row:self.row+self.window, self.column:self.column+self.window, 0] 
        green_window = a[self.row:self.row+self.window, self.column:self.column+self.window, 1] 
        
        red_signal = np.mean(red_window)
        green_signal = np.mean(green_window)
        
                   
        
                    
        
        data = pulseOx.get_data()
        
        data_dict = {'time'        :(datetime.now() - self.START_TIME).total_seconds(),
                     'camDataRed'  :red_signal,
                     'camDataGreen':green_signal,
                     'camBPMData'  :0,
                     'psData'      :data['pulseWaveform'],
                     'psBPMData'   :data['pulseRate']}        

        
        writer.save_to_csv(data_dict)
        
        tracker.track_performance(False, True)
        print('red signal = {}       green_signal = {}'.format(red_signal, green_signal))
        
        
        
        if RECORD_CAMERA:
            global frame_ctr, NUM_FRAMES, video_frames, time_array, pulse_array
            if (frame_ctr < NUM_FRAMES):
                # Store green
                video_frames[:, :, frame_ctr] = a[:, :, 1]
                # Store time associated w/ frame
                time_array[frame_ctr]  = data_dict['time']
                pulse_array[frame_ctr] = data_dict['psBPMData']
                
                frame_ctr = frame_ctr + 1
                print('recording camera feed')
        
    









## Lights setup
gpio.setmode(gpio.BCM)

pin = 0
if (LIGHT_COLOR == 'RED'):
    pin = RED_PIN
elif (LIGHT_COLOR == 'WHITE'):
    pin = WHITE_PIN

gpio.setup(pin, gpio.OUT)
gpio.output(pin, gpio.HIGH)



# Initialize arrays for storing trial values.
truth_bpms = []
red_bpms   = []
green_bpms = []
red_snrs   = []
green_snrs = []





# Initialize camera
if LOWER_RES:
    camera = picamera.PiCamera(resolution='640x480')
else:
    camera = picamera.PiCamera()

# Initialize video-storing array.
if RECORD_CAMERA: 
    NUM_FRAMES = 30*20
    res = camera.resolution
    video_frames = np.zeros((res.height, res.width, NUM_FRAMES), dtype=np.uint8)
    time_array   = np.zeros(NUM_FRAMES)
    pulse_array  = np.zeros(NUM_FRAMES)

    frame_ctr = 0




# Let the camera figure out good gain values, then fix the gain.
with DummyAnalyzer(camera) as analyzer:
    # Fix the camera's white-balance gains
    camera.awb_mode = 'off'
    camera.awb_gains = (1, 1)
    
    camera.start_recording(analyzer, 'rgb')
    try:
        camera.wait_recording(4)
        
    finally:
        camera.stop_recording()
        camera.exposure_mode = 'off'
         


for x in range(3):



    writer = PPG_Writer("recorded_data_{}".format(x))
    writer.start_writing()

    tracker = PerformanceTracker()    
    
    
    
    
    # Open / reopen the pulseOx serial port.
    pulseOx = CMS50D("/dev/ttyUSB0")
    
    
    if True:    

        # Construct the analysis output and start recording data to it
        with MyColorAnalyzer(camera) as analyzer:
            
            camera.start_recording(analyzer, 'rgb')
            tracker.reset()
            
            try:   
                camera.wait_recording(20)
                    
            finally:
                camera.stop_recording()
                RECORD_CAMERA = False
                

    ''' Post-single-trial-recording code '''
    pulseOx.close()
    
    ppg_analysis.main(writer)
    
    bpm_dict = ppg_analysis.get_bpm()
    truth_bpms.append(bpm_dict['truth'])
    red_bpms.append(  bpm_dict['red']  )
    green_bpms.append(bpm_dict['green'])
    
    snr_dict = ppg_analysis.get_snr()
    red_snrs.append(  snr_dict['red']  )
    green_snrs.append(snr_dict['green'])




# save video
if RECORD_CAMERA:
    print('saving...')
    np.savez('camera_recording.npz', video_frames=video_frames, time_array=time_array, pulse_array=pulse_array)
    print('done saving')


gpio.cleanup()

plt.title('BPM Graph')
plt.plot(truth_bpms, label="truth")
plt.plot(red_bpms  , '-r', label="red"  )
plt.plot(green_bpms, '-g', label="green")
plt.legend(loc="lower right")
plt.xlabel("Trial #")
plt.ylabel("BPM")
plt.show()

plt.title('SNR Graph')
plt.plot(red_snrs,   '-r', label='red'  )
plt.plot(green_snrs, '-g', label='green')
plt.legend(loc="lower right")
plt.xlabel("Trial #")
plt.ylabel("BPM")
plt.show()