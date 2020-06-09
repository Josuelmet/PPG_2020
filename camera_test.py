import RPi.GPIO as gpio
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2


# Debugging variables
TESTING_CONTINUOUS = True





#Code to track a loop's runtime and frequency
previous = time.time()
total_time = 0
count = 0
def track_performance():
    global previous, total_time, count
    
    now = time.time()
    
    print('loop took {} seconds'.format(now - previous))
    
    total_time = total_time + (now - previous)
    count = count + 1
    previous = time.time()
    
    print('Average loop frequency: {}'.format(count / total_time))





# camera lights setup
gpio.setmode(gpio.BCM)
gpio.setup(18, gpio.OUT)
gpio.output(18, gpio.HIGH)

# Initialize camera, grab reference tor aw camera capture
camera = PiCamera()
#camera.resolution = (480, 640)
rawCapture = PiRGBArray(camera)

# warm up the camera
time.sleep(0.1)



# Test FPS for camera.capture_continuous
# FPS = 8 at max resolution
# FPS = 20 at (640, 480)
if (TESTING_CONTINUOUS):
    for frame in camera.capture_continuous(rawCapture,
                                           format="bgr",
                                           use_video_port=True):
        # grab the raw NumPy array representing the image.
        image = frame.array
        
        # show the frame
        cv2.imshow("Frame", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        
        track_performance()
  
else:    
    # Test FPS for camera.capture()
    while (True):
        # grab the raw NumPy array representing the image.
        camera.capture(rawCapture, format="bgr", use_video_port=True)
        image = rawCapture.array
        
        
        cv2.imshow("Frame", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        
        track_performance()
    
    

gpio.cleanup()
cv2.destroyAllWindows()