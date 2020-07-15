import numpy as np
import cv2

import ppg_v7_analysis as ppg_analysis
from ppg_v7_writer import PPG_Writer


saved_data   = np.load('camera_recording.npz')
video_frames = saved_data['video_frames']
time_array   = saved_data['time_array']
pulse_array  = saved_data['pulse_array']



NUM_FRAMES = len(time_array)


def display_frames():
    for index in range(NUM_FRAMES):
        frame = video_frames[:, :, index]
        
        # Display frame
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
        
        print('time: {}'.format(time_array[index]))
    
    
    cv2.destroyAllWindows()
    
    
    
    
def get_results(row, column, window_size):
    
    writer = PPG_Writer('temp_window_data')
    writer.start_writing()
    
    for index in range(NUM_FRAMES):
        frame = video_frames[:, :, index]
        time  = time_array[index]
        pulse = pulse_array[index]
        
        # Extract the window from a monochrome frame.
        window = frame[row:row+window_size, column:column+window_size]
        signal = np.mean(window)
        
        
        data_dict = {'time'        :time,
                     'camDataRed'  :0,
                     'camDataGreen':signal,
                     'camBPMData'  :0,
                     'psData'      :0,
                     'psBPMData'   :pulse}        

        
        writer.save_to_csv(data_dict)
        
        
    from datetime import datetime
    start = datetime.now()
    ppg_analysis.main(writer)
    elapsed = (datetime.now() - start).total_seconds()
    print('elapsed time from analysis main: {}'.format(elapsed))
    return ppg_analysis.get_bpm()['green'], ppg_analysis.get_snr()['green']




for x in range(10):
    size = 250 - (25*x)
    #size = 30 - (3*x)
    bpm, snr = get_results(row=50, column=150, window_size=size)
    print('size={}, bpm={}, snr={:.2f}'.format(size, bpm, snr))
        
        
    