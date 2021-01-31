# PPG_2020

# Pipeline for version 9
# I) ppg_v9.py - the main executable file.
    1) Initialize the camera + lights. Set camera parameters.
    2) Instantiate a PPG_Writer object so that data can be recorded to a .csv file. Instantiate a CMS50D pulse oximeter object.
        NOTE: the default .csv filename is set as "reorded_data.csv".
              If you want to save multiple instances of the .csv data, you will have to change the names of the .csv files, or else they will overwrite each other.
    3) Receive camera frames in a constant loop via the MyColorAnalyzer object
        i) The loop extracts pixel intensity (PPG) data from each frame.
        ii) The loop then uses PPG_Writer to save the data to the .csv file.
        iii) The loop also saves each frame, its timestamp, and its associate pulse oximeter signal. This is done for later use by ppg_v9_pulsecam_recorder.py.
    4) Stop receiving frames and close the pulse oximeter port once TRIAL_DURATION seconds have passed.
    5) Call the code from ppg_v9_analysis.py by passing the PPG_Writer object from earlier.
       NOTE: If you want to see the plots from ppg_v9_analysis (including the HRV analysis), set DISPLAY to True in ppg_v9_analysis.
       Print out the resulting BPMs from the green and red channel. Also print the average ground truth BPM from the trial.
    6) Save the stored frames, timestamps, and pulse oximeter data by calling ppg_v9_pulsecam_recorder.py.
    
# II) ppg_v9_writer.py
    A helper file to make .csv input/output more modular.
    Each row of its .csv file pertains to one frame, and it contains the following data:
        a) time - Timestamp
        b) psData - Pulse oximeter waveform
        c) psBPMData - Pulse oximeter BPM
        d) camDataRed - Mean pixel intensity of certain region of red channel
        e) camDataGreen - Mean pixel intensity of certain region of green channel
        f) camBPMData - Unused leftover from earlier code. Is always 0. Should probably be deleted.
    The get_ functions (except for get_bpm) each return a list containing all the entries of a certain data column.
    e.g., get_cam_data_red() returns, as a list, the entire camDataRed column in the .csv file.
    
# III) ppg_v9_analysis.py
    Contains all the PPG timeseries Fourier analysis + plotting code.
    Results are plotted if DISPLAY is set to True.
    * Can be executed by itself. *
        By default, the file will analyze "recorded_data.csv", since this is the default name that ppg_v9 gives the .csv file containing data.
    1) Gets the raw PPG timeseries data (from the red and green channels) and sampling rate from the PPG_Writer object passed in.
    2) Linearly interpolates the data onto a uniform sampling rate of 30 Hz.
    3) Bandpass-filters the data with cutoff frequencies of [0.7, 4] Hz.
    4) Takes the FFT of the data. Finds the peak BPM, which becomes the BPM estimate.
    5) If DISPLAY is true, then run the HRV analysis.
    
# IV) ppg_v9_pulsecam_recorder.py
    Contains code extracted from the previous (PC) PulseCam recorder.
    Makes sure that the data found in ppg_v9.py is saved in a format compatible with the PulseCam algorithm.
    The PulseCam-relevant data for the N-th experiment is stored in [current working directory]/dump/N.
    1) make_data_folder()
        a) Find 'dump' folder in the current working directory. Instantiate the 'dump' folder if it does not exist already.
        b) Assign a default ID of 0 to the current experiment. If there are no other folders named '0' in 'dump', then instantiate the folder dump/0.
           If dump/0 already exists, then keep incrementing the ID number X until dump/X does not exist.
              For example, if dump/0, dump/1, ..., dump/10 all exist, then the current experiment will be saved under dump/11.
        c) Instantiate the folders dump/[ID]/Webcam and dump/[ID]/PulseOX.
    2) record_pulseox(waveform, time)
        Small NOTE: 'waveform' and 'time' were stored during ppg_v9.py separately from the .csv file, although record_pulseox() could/should probably be refactored to just use the PPG_Writer object, since it already contains the pulse oximeter's waveform and its associated timestamps.
        a) Resample 'waveform' and 'time' to a uniform 30 Hz sampling rate.
        b) Save the two resampled lists, and their length, in .pkl and .mat files. The two files can be found in dump/[ID]/PulseOX.
    3) record_camera(images, time, trial_duration)
        a) Save each image as a PNG in dump/[ID]/Webcam.
        b) Save the following as .pkl and .mat files in dump/[ID]/Webcam :
            i) each frame's timestamp
            ii) total number of frames
            iii) image width
            iv) image height
            v) experiment duration, which just equals TRIAL_DURATION.
            
# Miscellaneous Files
    performancetracker.py
        It simply prints how fast a loop is running.
        It allows for monitoring of the frequency of the camera loop while ppg_v9 is running.
            a) print_period=True prints the elapsed time each loop takes to run.
            b) print_frequency=True prints the average loop frequency, which should converge to 30 Hz, since this is the ideal sampling rate of the camera loop.
    
    pulseoximeter.py - interface for CMS50D pulse oximeter.
    
    calibration.py 
        Receives frames from the camera and displays them, so that the user can make sure that the LEDs and PPG pixel window are properly placed.
        Also allows for experimentation with camera settings, since the user can directly see how those settings affect the image quality.             
        

# v8 vs v9
Versions 8 and 9 have the same pipeline.
The main difference between v8 and v9 has to do with how the camera's parameters (gain, exposure, etc.) are set.

In v8, the camera runs for ~2 seconds (in the DummyAnalyzer camera loop) before starting to capure PPG data.
The 2 seconds give the camera time to set its gain and exposure automatically, after which those settings are fixed.

In v9, the camera does not need time to calibrate itself.
Additional code in ppg_v9.py allows for the camera's ISO and gain settings to be set directly.
