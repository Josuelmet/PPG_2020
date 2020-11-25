import os
import numpy as np
from scipy import io
import pickle
import cv2

from scipy.interpolate import interp1d


# To be initialized in make_data_folder().
webcam_folder = None
pulseOx_folder = None


def make_data_folder():
    global webcam_folder, pulseOx_folder
    
    dataDump_base = os.path.join(os.getcwd(),'dump')
    if not os.path.exists(dataDump_base):
        os.makedirs(dataDump_base)
        
        
    p_id = 0
    done = False
    while not done:
        pid_folder = os.path.join(dataDump_base, str(p_id))
        if os.path.exists(pid_folder):
            print('Experiment name {} already used, try something new'.format(p_id))
            p_id = p_id + 1
            done = False
        else:
            os.makedirs(pid_folder)
            done = True
        
        
    webcam_folder = os.path.join(pid_folder, 'Webcam')
    pulseOx_folder = os.path.join(pid_folder, 'PulseOX')
    if not os.path.exists(webcam_folder):
        os.makedirs(webcam_folder)
    if not os.path.exists(pulseOx_folder):
        os.makedirs(pulseOx_folder)

    return




def record_pulseox(waveform, time):
    '''
    # Begin resampling
    new_fs = 30
    sampling_interval = 1 / new_fs

    # Quantize beginning + ending time to the nearest multiple of sampling_interval.
    initial_time = int(time[0] * new_fs) / new_fs
    end_time = int(time[-1] * new_fs) / new_fs

    # Figure out number of samples.
    elapsed_time = end_time - initial_time
    num_samples = int(elapsed_time * new_fs) + 1

    # Generate uniform time scale
    uniform_time = np.linspace(initial_time, end_time, num=num_samples, endpoint=True)
    
    # Resample pulse oximeter to be exactly 30 Hz.
    f_pox = interp1d(time, waveform, fill_value="extrapolate")
    resampled_pox = f_pox(uniform_time)
    '''
    
    pxID = 'px1'
    
    data = {}
    data['pulseOxRecord'] = waveform #resampled_pox
    data['pulseOxTime'] = time #uniform_time
    data['numPulseSample'] = len(data['pulseOxTime'])

    f = open(os.path.join(pulseOx_folder, pxID + '_full.pkl'), 'wb') # 'wb' will overwrite everytime
    # 'wb' will overwrite everytime
    pickle.dump(data, f)
    f.close()
    
    # write a .mat file
    with open(os.path.join(pulseOx_folder, pxID + '_full.mat'), 'wb') as f:
        io.savemat(f, data)
    
    return




def record_camera(images, time, trial_duration):
    camID = 'webcam'
    
    imageFolder = os.path.join(webcam_folder, camID)
    if not os.path.exists(imageFolder):
        os.makedirs(imageFolder)
        
    frameCounter = 0
    
    # store the camera frames
    print('Storing camera frames....')
    while images:
        frame_perfusion = np.array(images.popleft())
        frame_perfusion = cv2.cvtColor(frame_perfusion, cv2.COLOR_RGB2BGR)
            
        frameFile = os.path.join(imageFolder,'frame_{0:05d}.png'.format(frameCounter))
        cv2.imwrite(frameFile, frame_perfusion)
        
        frameCounter+=1
    

    
    
    # Store the other camera data
    data = {}
    data['cameraTime'] = np.array(time)
    data['numFrames'] = frameCounter
    data['imageWidth'] = frame_perfusion.shape[0]
    data['imageHeight'] = frame_perfusion.shape[1]
    data['trialDuration'] = trial_duration
    
    
    f = open(os.path.join(webcam_folder, camID + '_full.pkl'), 'wb') # 'wb' will overwrite everytime
    pickle.dump(data, f)
    f.close()
    
    
    # write a .mat file
    with open(os.path.join(webcam_folder, camID + '_full.mat'), 'wb') as f:
        io.savemat(f, data)
    
    return



