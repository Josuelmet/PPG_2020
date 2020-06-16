"""
CLass to save PPG data to a CSV file.
"""
from datetime import datetime
import io

## Heartrate analysis package
import heartpy as hp
from heartpy.exceptions import BadSignalWarning


class PPG_Writer(object):
    
    def __init__(self, csvStr=None):
        # Setup CSV File
        now = datetime.now()
        
        if csvStr is None:
            self.filename = 'ppg_' + now.strftime("%Y-%m-%d_%I_%M_%S")
        else:
            self.filename = csvStr + '_' + now.strftime("%Y-%m-%d_%I_%M_%S")
            
        self.filename = self.filename + ".csv"
        
        headers = (u'time' + ',' + u'ps_waveform' + ',' + u'ps_bpm' + ',' + u'cam_waveform' + ',' + u'cam_bpm')
        
        with io.open(self.filename, 'w', newline='') as f:
            f.write(headers)
            f.write(u'\n')
    
    
    def save_to_csv(self, data):
        with io.open(self.filename, "a", newline="") as f:
            
            row = str(data['time'][-1])    + "," + \
                  str(data['psData'][-1])  + "," + str(data['psBPMData'][-1]) + "," + \
                  str(data['camData'][-1]) + "," + str(data['camBPMData'][-1])
            
            f.write(row)
            f.write("\n")
            
    
    def get_samplerate(self):
        loaded_times = hp.get_data(self.filename, column_name='time')
        fs = hp.get_samplerate_datetime(loaded_times, '%S.%f')
        return fs
    
    def get_cam_data(self):
        camData = hp.get_data(self.filename, column_name='cam_waveform')
        return camData
    
    def get_time_data(self):
        timeData = hp.get_data(self.filename, column_name='time')
        return timeData
        
    def get_bpm_estimate(self, time_data, cam_data):
        
        fps = hp.get_samplerate_datetime(time_data, '%S.%f')
        
        cam_bpm = 0
        
        filtered_ppg_r = hp.filter_signal(cam_data, 
                                          cutoff = [0.8, 1], 
                                          filtertype = 'bandpass',
                                          sample_rate = fps, 
                                          order = 4,
                                          return_top = False)
        try:
            working_data, measures = hp.process(cam_data, fps)
        except BadSignalWarning:
            print("Bad signal")
        else:
            if (measures['bpm'] > 40 and measures['bpm'] < 180):
                cam_bpm = measures['bpm']
                    
                    
        return filtered_ppg_r, cam_bpm
        