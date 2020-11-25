import numpy as np
import matplotlib.pyplot as plt

import heartpy as hp

from scipy.signal import find_peaks
from scipy.interpolate import interp1d

from ppg_v9_writer import PPG_Writer
from performancetracker import PerformanceTracker

import sys
HRV_LOCATION = '/home/pi/Desktop/hrv'
sys.path.insert(1, HRV_LOCATION)
from hrv_function import hrv_function



# Variable indicating whether or not the data + results should be graphed.
DISPLAY = False
if __name__ == "__main__":
    DISPLAY = True    


# Initialize dictionaries
bpms = {'truth':None, 'red':None, 'green':None}
snrs = {'red':None, 'green':None}


def main(writer):
    """
    A function to extract the bpm from PPG data in a .csv file.
    
    Parameters
    ----------
    writer: PPG_Writer
            A PPG_Writer object initialized with the desired .csv file.
    """
    global bpms, snrs
    
    '''
    Get/Display raw data and sampling rate.
    '''
    # Acquire time-series data from the .csv file
    # Ignore the first second of data, since it's very different from the other data.
    timeData     = writer.get_time_data()[30:]
    camDataRed   = writer.get_cam_data_red()[30:]
    camDataGreen = writer.get_cam_data_green()[30:]
    pulseData    = writer.get_pulseox_data()[30:]

    # Acquire sampling rate and ground truth BPM from the .csv file
    sampling_rate = hp.get_samplerate_datetime( timeData, '%S.%f')
    BPM_TRUTH = writer.get_bpm()


    # If desired, graph the raw PPG time-series data for both channels.
    if DISPLAY:
        plt.title("Raw PPG Data")
        #plt.plot(timeData, camDataRed,   "-r", label="Red")
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

    # Quantize beginning + ending time to the nearest multiple of sampling_interval.
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

    # Filter the interpolated PPG signals with a [0.7, 4] Hz bandpass filter.
    LOWER_CUTOFF = 0.7
    UPPER_CUTOFF = 4
    new_red = hp.filter_signal(new_red,
                               cutoff = [LOWER_CUTOFF, UPPER_CUTOFF], 
                               filtertype = 'bandpass',
                               sample_rate = new_fs,
                               order = 4,
                               return_top = False)

    new_green = hp.filter_signal(new_green,
                                 cutoff = [LOWER_CUTOFF, UPPER_CUTOFF], 
                                 filtertype = 'bandpass',
                                 sample_rate = new_fs,
                                 order = 4,
                                 return_top = False)

    # If desired, graph the filtered PPG time-series for both color channels.
    if DISPLAY:
        plt.title("Filtered PPG Data")
        #plt.plot(uniform_time, new_red,   '-r', label='Red')
        plt.plot(uniform_time, new_green, '-g', label='Green')
        plt.legend(loc="lower right")
        plt.ylabel("Mean Pixel Intensity")
        plt.xlabel("Time (seconds)")
        plt.show()
    




    '''
    Take FFT of PPGs
    '''
    # Calculate FFT magnitude of both PPG signals.
    # Remove frequencies above the sampling frequency.
    fft_red   = np.fft.fft(new_red)   / N
    fft_green = np.fft.fft(new_green) / N
    fft_red   = fft_red[  range(N//2)]
    fft_green = fft_green[range(N//2)]
    fft_red   = abs(fft_red)
    fft_green = abs(fft_green)

    # Get frequency axis corresponding to the FFTs.
    values = np.arange(N // 2)
    timePeriod = N * sampling_interval
    frequencies = values / timePeriod


    
    # Find indices corresponding to f_bpm-0.1, f_bpm, and f_bpm+0.1,
    # Where f_bpm = the ground truth BPM in Hz.
    f_bpm = BPM_TRUTH / 60
    bpm_index   = np.abs(frequencies - f_bpm).argmin()
    upper_index = np.abs(frequencies - f_bpm - 0.1).argmin()
    lower_index = np.abs(frequencies - f_bpm + 0.1).argmin()
    
    # Find the peaks of the FFTs for both color channels.
    red_peak_index = np.argmax(fft_red)
    red_bpm = int(frequencies[red_peak_index] * 60)

    green_peak_index = np.argmax(fft_green)
    green_bpm = int(frequencies[green_peak_index] * 60)

    '''
    Calculate SNR
    '''
    # Find indices corresponding to the cutoff frequencies of the bandpass filter from earlier.
    lower_cutoff_index = np.abs(frequencies - LOWER_CUTOFF).argmin()
    upper_cutoff_index = np.abs(frequencies - UPPER_CUTOFF).argmin()

    red_signal = 0
    red_noise = 0
    green_signal = 0
    green_noise = 0
    
    # Iterate through all indices between the lower and upper cutoff frequencies
    for x in range(lower_cutoff_index, upper_cutoff_index + 1):
        # If current index's frequency is close to the ground truth BPM frequency,
        # then add its power (magnitude squared) to the signal variable.
        if (x >= lower_index and x <= upper_index):
            red_signal = red_signal + fft_red[x]**2
            green_signal = green_signal + fft_green[x]**2
        # Else, add its power to the noise variable.
        else:
            red_noise = red_noise + fft_red[x]**2
            green_noise = green_noise + fft_green[x]**2
            
    red_snr = red_signal / red_noise
    green_snr = green_signal / green_noise

    print('ppg analysis done')
    
    
    bpms = {'truth':BPM_TRUTH, 'red':red_bpm, 'green':green_bpm}
    snrs = {'red':red_snr, 'green':green_snr}
    
    
    
    # If desired, graph the FFTs of both color channels,
    # with dots indicating the frequencies of the BPM estimates and ground truth.
    if DISPLAY:
        '''
        plt.title('Red FFT. BPM Estimate = {},Truth = {}'.format(red_bpm, BPM_TRUTH))
        plt.plot(frequencies, fft_red)
        plt.ylabel('Spectral Power')
        plt.xlabel('Frequency (Hz)')
    
        plt.plot(frequencies[red_peak_index], fft_red[red_peak_index], 'ro', label='Estimate')
        plt.plot(frequencies[bpm_index],      fft_red[bpm_index],      'go', label='Reality')
        plt.legend(loc='upper right')
        plt.show()
        '''
        
        plt.title('Green FFT. BPM Estimate = {},Truth = {}'.format(green_bpm, BPM_TRUTH))
        plt.plot(frequencies, fft_green)
        plt.ylabel('Spectral Power')
        plt.xlabel('Frequency (Hz)')
        
        plt.plot(frequencies[green_peak_index], fft_green[green_peak_index], 'ro', label='Estimate')
        plt.plot(frequencies[bpm_index],        fft_green[bpm_index],        'go', label='Reality')
        plt.legend(loc='upper right')
        plt.show()
        
    
    # If desired, graph the results from the heart rate variability algorithm,
    # with the input being the green channel signal,
    # and plot the pulseox hrv for comparison.
    if DISPLAY:
        
        # PulseOx interpolation and filtering
        f_pox = interp1d(timeData, pulseData, fill_value="extrapolate")
        new_pox = hp.filter_signal(f_pox(uniform_time),
                                   cutoff = [LOWER_CUTOFF/4, UPPER_CUTOFF], 
                                   filtertype = 'bandpass',
                                   sample_rate = new_fs, #sampling_rate 
                                   order = 4,
                                   return_top = False)
        
        
        # PulseOx FFT and BPM Estimation
        fft_pox   = abs(np.fft.fft(new_pox) / N)
        fft_pox   = fft_pox[range(N//2)]
        pox_bpm = int(frequencies[np.argmax(fft_pox)] * 60)
        
        print('pulse ox bpm: {}'.format(pox_bpm))
        print('ground truth: {}'.format(BPM_TRUTH))
        
        '''
        plt.plot(uniform_time, f_pox(uniform_time))
        plt.show()
        '''
        
        performance_tracker = PerformanceTracker()
        # Calculate + plot pulse oximeter hrv
        hrv, thrv, lfcam, hfcam, lf_hfcam, BRcam, sdnncam, sdsdcam, rmssdcam = hrv_function(new_pox,
                                                                                            fs=int(30*BPM_TRUTH/pox_bpm),
                                                                                            bpm=BPM_TRUTH)
        performance_tracker.track_performance()
        pox_hrv = hrv
        pox_thrv = thrv
        print('Pulse Ox Statistics:')
        print('lfcam: {:.2f}'.format(lfcam))
        print('hfcam: {:.2f}'.format(hfcam))
        print('lf_hfcam: {:.2f}'.format(lf_hfcam))
        print('BRcam: {:.2f}'.format(BRcam))
        print('sdnncam: {:.2f}'.format(sdnncam))
        print('sdsdcam: {:.2f}'.format(sdsdcam))
        print('rmssdcam: {:.2f}'.format(rmssdcam))        
        print()
        print()
        
        performance_tracker.reset()
        # Calculate + plot green channel hrv
        num = int( len(new_green) * pox_bpm / BPM_TRUTH )
        hrv, thrv, lfcam, hfcam, lf_hfcam, BRcam, sdnncam, sdsdcam, rmssdcam = hrv_function(new_green[:num],
                                                                                            fs=30,
                                                                                            bpm=green_bpm)
        performance_tracker.track_performance()
        print('PPG Statistics:')
        print('lfcam: {:.2f}'.format(lfcam))
        print('hfcam: {:.2f}'.format(hfcam))
        print('lf_hfcam: {:.2f}'.format(lf_hfcam))
        print('BRcam: {:.2f}'.format(BRcam))
        print('sdnncam: {:.2f}'.format(sdnncam))
        print('sdsdcam: {:.2f}'.format(sdsdcam))
        print('rmssdcam: {:.2f}'.format(rmssdcam))

        
        
        
        plt.title("BPM as a function of HRV Algorithm")
        plt.plot(thrv/1000,     60000/hrv,     label="ppg")
        plt.plot(pox_thrv/1000, 60000/pox_hrv, label="pulseox")
        plt.xlabel("Time Window 30s")
        plt.ylabel("BPM")
        plt.legend(loc="lower right")
        plt.show()        
        
        
        '''
        # pulseox resampling
        f_pox = interp1d(uniform_time*pox_bpm/BPM_TRUTH, new_pox, bounds_error=False)
        new_pox = f_pox(uniform_time)
        new_pox = new_pox[new_pox == new_pox]
        
        hrv, thrv, lfcam, hfcam, lf_hfcam, BRcam, sdnncam, sdsdcam, rmssdcam = hrv_function(new_pox,
                                                                                            fs=30,
                                                                                            bpm=BPM_TRUTH)        
        plt.plot(thrv/1000, 60000/hrv, label="pulseox reresampled")
        '''
        
        
        

def get_bpm():
    return bpms
    
def get_snr():
    return snrs





if __name__ == "__main__":
    main(PPG_Writer("recorded_data"))
    