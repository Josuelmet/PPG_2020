import time
import numpy as np
from datetime import datetime
from collections import deque

import picamera
from picamera.array import PiRGBAnalysis
from picamera import mmal, mmalobj, exc
from picamera.mmalobj import to_rational

# For pulse oximeter
from pulseoximeter import CMS50D

# For camera lights
import RPi.GPIO as gpio

from performancetracker import PerformanceTracker
from ppg_v9_writer import PPG_Writer
import ppg_v9_analysis as ppg_analysis
from ppg_v9_pulsecam_recorder import *




# Program execution variables
LOWER_RES = True
PULSECAM = True

TRIAL_DURATION = 31
FPS = 30 # Highest FPS possible is 32.




       
def set_gain(camera, analog=1, digital=1):
    
    MMAL_PARAMETER_ANALOG_GAIN = mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x59
    MMAL_PARAMETER_DIGITAL_GAIN = mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x5A
    
    ret1 = mmal.mmal_port_parameter_set_rational(camera._camera.control._port,
                                                 MMAL_PARAMETER_ANALOG_GAIN,
                                                 to_rational(analog))
    ret2 = mmal.mmal_port_parameter_set_rational(camera._camera.control._port,
                                                 MMAL_PARAMETER_DIGITAL_GAIN,
                                                 to_rational(digital))
    
    if ret1 == 4 or ret2 == 4:
        raise exc.PiCameraMMALError(ret, "Are you running the latest version of the userland libraries?")
    elif ret1 != 0 or ret2 != 0:
        raise exc.PiCameraMMALError(ret)



# Define a ColorAnalyzer to handle high-speed frame acquisition.
# The analyze(self, a) function is called each time that the
# camera outputs a frame.
class MyColorAnalyzer(PiRGBAnalysis):
    def __init__(self, _camera):
        super(MyColorAnalyzer, self).__init__(_camera)
        
        # Initialize the signal window parameters,
        # depending on the resolution of the camera.
        if LOWER_RES:
            self.row    = 50
            self.column = 150
            self.window = 250
        else:
            self.row    = 150
            self.column = 300
            self.window = 400
        
        # Record the starting time
        self.START_TIME = datetime.now()
        
        # Define FPS variables
        self.period = 1/FPS
        self.t = time.time()
      
      

      

    def analyze(self, a):
        """
        Handle the current frame sent from the camera.
        Take the intensity means of the previously defined signal window
        for both the red and the green channels.
        Receive the current output from the pulse oximeter.
        Store the pulse oximeter + relevant camera data in a .csv file.
        Record the current frame if desired.
        
        Parameters
        ----------
        self: MyColorAnalyzer
        a: Array
           The current frame sent from the camera.
        """
        global camDataRed, camDataGreen, camBPMData, psData, psBPMData, time, camera        

        # Extract red- and green-channel signal windows from the frame.
        red_window = a[self.row:self.row+self.window, self.column:self.column+self.window, 0] 
        green_window = a[self.row:self.row+self.window, self.column:self.column+self.window, 1] 
        
        # Take window means
        red_signal = np.mean(red_window)
        green_signal = np.mean(green_window)
        
                   
        
                    
        # Receive data from the pulse oximeter.
        data = pulseOx.get_data()
        
        # Store relevant data in a dictionary.
        data_dict = {'time'        :(datetime.now() - self.START_TIME).total_seconds(),
                     'camDataRed'  :red_signal,
                     'camDataGreen':green_signal,
                     'camBPMData'  :0,
                     'psData'      :data['pulseWaveform'],
                     'psBPMData'   :data['pulseRate']}        

        # Store data in a .csv file
        writer.save_to_csv(data_dict)
        
        # Print some relevant performance metrics
        tracker.track_performance(False, True)
        
        
        
        if PULSECAM:
            global video_frames, pulseox_time, pulseox_wave
            
            video_frames.append(a)
            pulseox_time.append(data_dict['time'])
            pulseox_wave.append(data_dict['psData'])
        
        # Try to limit FPS to a set constant
        self.t += self.period
        time.sleep(max(0, self.t-time.time()))
    









# Initialize / turn on Raspberry PI GPIO lights
gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.OUT)
gpio.output(21, gpio.HIGH)

# Initialize the camera
if LOWER_RES:
    camera = picamera.PiCamera(resolution='640x480', framerate=30)
else:
    camera = picamera.PiCamera()

# Initialize data storage structures.
if PULSECAM:
    video_frames = deque()
    pulseox_time = deque()
    pulseox_wave = deque()





# Set ISO, awb_gains to the desired values
set_gain(camera, analog=5, digital=0)
camera.iso = 100
camera.awb_mode = 'off'
camera.awb_gains = (1.0,1.0)
# Now fix the values
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
time.sleep(1)


# Open and initialize a .csv file named recorded_data
writer = PPG_Writer("recorded_data")
writer.start_writing()
    
# Initialize performance metric tracker
tracker = PerformanceTracker()    
      
# Open / reopen the pulseOx serial port.
pulseOx = CMS50D("/dev/ttyUSB0")
    
    
    
    
# Construct the analysis output and start recording data to it
with MyColorAnalyzer(camera) as analyzer:
        
    # Begin recording rgb frames from the camera.
    camera.start_recording(analyzer, 'rgb')
    # Reset PerformanceTracker
    tracker.reset()
        
    try:
        # Receive frames for TRIAL_DURATION seconds.
        camera.wait_recording(TRIAL_DURATION)
        
    finally:
        # Stop receiving camera frames.
        camera.stop_recording()
                

''' Post-recording code '''
# Close pulse oximeter serial port because the pulse oximeter
# outputs data at 60 Hz, while the MyColorAnalyzer analyze()
# function is usually called at only 30 Hz.
# The disparity results in the pulse oximeter lagging behind
# the PPG signal.
# Hence the pulse oximeter needs to be continuously closed
# and re-opened, so as to reset the pulse oximeter's buffer.
pulseOx.close()
    
# Run PPG signal analysis code to get the bpm of the current PPG signal
ppg_analysis.main(writer)
    
# Get the ground truth, red-channel, and green-channel BPMs of the current PPG signal.
# Store each BPM in a list.
bpm_dict = ppg_analysis.get_bpm()
    
truth_bpm = bpm_dict['truth']
red_bpm = bpm_dict['red']
green_bpm = bpm_dict['green']
    
print('Truth BPM: {}'.format(truth_bpm))
print('Red BPM:   {}'.format(red_bpm))
print('Green BPM: {}'.format(green_bpm))



    
if PULSECAM:
    print('saving...')
    make_data_folder()
    record_pulseox(pulseox_wave, pulseox_time)
    record_camera(video_frames, pulseox_time, TRIAL_DURATION)
    print('done saving')


# Close GPIO
gpio.cleanup()

print()
print('camera exposure:')
print(camera.exposure_speed)
print('shutter speed (microseconds):')
print(camera.shutter_speed)