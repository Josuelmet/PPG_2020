import numpy as np
import matplotlib.pyplot as plt

import heartpy as hp
from scipy.signal import find_peaks

from scipy.interpolate import interp1d

from ppg_v7_writer import PPG_Writer



DISPLAY = False
if __name__ == "__main__":
    DISPLAY = True    



bpms = {'truth':None, 'red':None, 'green':None}
snrs = {'red':None, 'green':None}

def main(writer):
    global bpms, snrs
    
    '''
    Get/Display raw data and sampling rate.
    '''

    # Ignore the first second of data, since it's very different from the other data.
    timeData     = writer.get_time_data()[30:]
    camDataRed   = writer.get_cam_data_red()[30:]
    camDataGreen = writer.get_cam_data_green()[30:]
    pulseData    = writer.get_pulseox_data()[30:]

    sampling_rate = hp.get_samplerate_datetime( timeData, '%S.%f')
    BPM_TRUTH = writer.get_bpm()


    if DISPLAY:
        plt.title("Raw PPG Data")
        plt.plot(timeData, camDataRed, "-r", label="Red")
        plt.plot(timeData, camDataGreen, "-g", label="Green")
        plt.legend(loc="lower right")
        plt.ylabel("Mean Pixel Intensity")
        plt.xlabel("Time (seconds)")
        plt.show()

        
        
    
    '''
    Interpolate PPG signals
    '''
    new_fs = 30
    sampling_interval = 1 / new_fs

    # Quantize time
    initial_time = int(timeData[0] * new_fs) / new_fs
    end_time = int(timeData[-1] * new_fs) / new_fs

    # Figure out number of samples.
    elapsed_time = end_time - initial_time
    num_samples = int(elapsed_time * new_fs) + 1


    # Generate uniform time scale and interpolation function
    uniform_time = np.linspace(initial_time, end_time, num=num_samples, endpoint=True)
    f_red   = interp1d(timeData, camDataRed,   fill_value="extrapolate")
    f_green = interp1d(timeData, camDataGreen, fill_value="extrapolate")


    # Use interpolation function to generate wave.
    new_red   = f_red(  uniform_time)
    new_green = f_green(uniform_time)
    N = len(new_red)

    


    '''
    Filter/Enhance Signals
    '''

    # Display the filtered PPG, print the heartpy bpm estimate
    LOWER_CUTOFF = 0.7
    UPPER_CUTOFF = 4
    #filtered_red_ppg = hp.filter_signal(camDataRed, 
    new_red = hp.filter_signal(new_red,
                                        cutoff = [LOWER_CUTOFF, UPPER_CUTOFF], 
                                        filtertype = 'bandpass',
                                        sample_rate = new_fs, #sampling_rate 
                                        order = 4,
                                        return_top = False)

    #filtered_green_ppg = hp.filter_signal(camDataGreen,
    new_green = hp.filter_signal(new_green,
                                          cutoff = [LOWER_CUTOFF, UPPER_CUTOFF], 
                                          filtertype = 'bandpass',
                                          sample_rate = new_fs, #sampling_rate 
                                          order = 4,
                                          return_top = False)

    if DISPLAY:
        plt.title("Filtered PPG Data")
        plt.plot(uniform_time, new_red,   '-r', label='Red')
        plt.plot(uniform_time, new_green, '-g', label='Green')
        #plt.plot(timeData, filtered_red_ppg, "-r", label="Red")
        #plt.plot(timeData, filtered_green_ppg, "-g", label="Green")
        plt.legend(loc="lower right")
        plt.ylabel("Mean Pixel Intensity")
        plt.xlabel("Time (seconds)")
        plt.show()
    




    '''
    Take FFT of PPGs
    '''
    # Take FFT of waves. Remove frequencies above the sampling frequency.
    fft_red   = np.fft.fft(new_red)   / N
    fft_green = np.fft.fft(new_green) / N
    fft_red   = fft_red[  range(N//2)]
    fft_green = fft_green[range(N//2)]
    fft_red   = abs(fft_red)
    fft_green = abs(fft_green)

    # Get frequency spectrum of FFTs.
    values = np.arange(N // 2)
    timePeriod = N * sampling_interval
    frequencies = values / timePeriod


    
    # Find indices of bpm spike.
    f_bpm = BPM_TRUTH / 60
    bpm_index   = np.abs(frequencies - f_bpm).argmin()
    upper_index = np.abs(frequencies - f_bpm - 0.1).argmin()
    lower_index = np.abs(frequencies - f_bpm + 0.1).argmin()
    
    
    red_peak_index = np.argmax(fft_red)
    red_bpm = int(frequencies[red_peak_index] * 60)

    green_peak_index = np.argmax(fft_green)
    green_bpm = int(frequencies[green_peak_index] * 60)

    '''
    Calculate SNR
    '''
    lower_cutoff_index = np.abs(frequencies - LOWER_CUTOFF).argmin()
    upper_cutoff_index = np.abs(frequencies - UPPER_CUTOFF).argmin()

    red_signal = 0
    red_noise = 0
    green_signal = 0
    green_noise = 0

    for x in range(lower_cutoff_index, upper_cutoff_index + 1):
        if (x >= lower_index and x <= upper_index):
            red_signal = red_signal + fft_red[x]**2
            green_signal = green_signal + fft_green[x]**2
        else:
            red_noise = red_noise + fft_red[x]**2
            green_noise = green_noise + fft_green[x]**2
            
    red_snr = red_signal / red_noise
    green_snr = green_signal / green_noise

    print('ppg analysis done')
    
    
    bpms = {'truth':BPM_TRUTH, 'red':red_bpm, 'green':green_bpm}
    snrs = {'red':red_snr, 'green':green_snr}
    
    
    
    
    if DISPLAY:
        plt.title('Red FFT. Estimate = {},Truth = {}'.format(red_bpm, BPM_TRUTH))
        plt.plot(frequencies, fft_red)
        plt.ylabel('Spectral Power')
        plt.xlabel('Frequency (Hz)')
        
        plt.plot(frequencies[red_peak_index], fft_red[red_peak_index], 'ro', label='Estimate')
        plt.plot(frequencies[bpm_index],      fft_red[bpm_index],      'go', label='Reality')
        plt.legend(loc='upper right')
        plt.show()
        
        
        plt.title('Green FFT. Estimate = {},Truth = {}'.format(green_bpm, BPM_TRUTH))
        plt.plot(frequencies, fft_green)
        plt.ylabel('Spectral Power')
        plt.xlabel('Frequency (Hz)')
        
        plt.plot(frequencies[green_peak_index], fft_green[green_peak_index], 'ro', label='Estimate')
        plt.plot(frequencies[bpm_index],        fft_green[bpm_index],        'go', label='Reality')
        plt.legend(loc='upper right')
        plt.show()
        
    


def get_bpm():
    return bpms
    
def get_snr():
    return snrs




if __name__ == "__main__":
    FILENAME = "recorded_data_2"
    #FILENAME = 'temp_window_data'
    writer = PPG_Writer(FILENAME)
    main(writer)
    print('done')