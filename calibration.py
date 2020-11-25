import picamera
from picamera.array import PiRGBAnalysis
from picamera import mmal, mmalobj, exc
from picamera.mmalobj import to_rational

# For camera lights
import RPi.GPIO as gpio

import numpy as np
import cv2
import time



## Lights setup
gpio.setmode(gpio.BCM)

pin = 21 # White pin.
gpio.setup(pin, gpio.OUT)
gpio.output(pin, gpio.HIGH)

pin = 12 # Red pin.
gpio.setup(pin, gpio.OUT)
gpio.output(pin, gpio.HIGH)

destroyed = False


class MyColorAnalyzer(PiRGBAnalysis):
    def __init__(self, _camera):
        super(MyColorAnalyzer, self).__init__(_camera)

        '''
        self.row=150
        self.column=300
        self.window=400
        '''
        self.row=50
        self.column=150
        self.window=250
        

    def analyze(self, a):
        global destroyed
        
        if (not destroyed):
            signal_window = a[self.row:self.row+self.window, self.column:self.column+self.window, :]
            
            # bgr format to make opencv code easier
            red   = np.mean(signal_window[:, :, 2])
            green = np.mean(signal_window[:, :, 1])
            blue  = np.mean(signal_window[:, :, 0])
            
            cv2.imshow("Frame", self.draw_window(a))
            
            gray_window = cv2.cvtColor(signal_window, cv2.COLOR_BGR2GRAY)
            avg, contrast = cv2.meanStdDev(gray_window)
            avg = avg[0][0]
            contrast = contrast[0][0]
            
            
            print('Contrast = {:.1f}'.format(contrast))
            print('Red      = {:.1f},    Green = {:.1f},    Blue = {:.1f}'.format(red, green, blue))

        
        if (cv2.waitKey(1) == ord('q')):
            cv2.destroyWindow("Frame")
            destroyed = True
        


    
    def draw_window(self, a):
        row1 = self.row
        row2 = self.row + self.window
        col1 = self.column
        col2 = self.column + self.window
        
        frame = np.copy(a)
        for color_index in range(3):
            for row in range(row1, row2):
                for i in range(4):
                    frame[row, col1-i, color_index] = 255
                    frame[row, col2+i, color_index] = 255
                
            for col in range(col1, col2):
                for i in range(4):
                    frame[row1-i, col, color_index] = 255
                    frame[row2+i, col, color_index] = 255
        return frame
    



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


camera = picamera.PiCamera(resolution='640x480', framerate=30)
# Set ISO, awb_gains to the desired values
set_gain(camera, analog=5, digital=0)
camera.iso = 100
camera.awb_mode = 'off'
camera.awb_gains = (1.0,1.0)
# Now fix the values
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'




# Finally, take video with the fixed settings
with MyColorAnalyzer(camera) as analyzer:

    camera.start_recording(analyzer, 'bgr')
            
    try:
        while (not destroyed):
            camera.wait_recording(1)
    finally:
        camera.stop_recording()
         
         
         
         


''' Post-recording code '''
print('stopped recording...')
gpio.cleanup()
cv2.destroyAllWindows()



print()
print('camera exposure:')
print(camera.exposure_speed)
print('shutter speed (microseconds):')
print(camera.shutter_speed)