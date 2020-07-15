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
            self.filename = csvStr
            
        self.filename = self.filename + ".csv"
        
    
    def start_writing(self):
        
        # Save a new CSV file to write to.
        headers = (u'time' + ',' + u'ps_waveform' + ',' + u'ps_bpm' + ',' + \
                   u'cam_waveform_red' + ',' + u'cam_waveform_green' + ',' + u'cam_bpm')
        
        with io.open(self.filename, 'w', newline='') as f:
            f.write(headers)
            f.write(u'\n')
    
    '''
    def save_to_csv(self, data):
        with io.open(self.filename, "a", newline="") as f:
            
            row = str(data['time'][-1])       + "," + \
                  str(data['psData'][-1])     + "," + str(data['psBPMData'][-1])    + "," + \
                  str(data['camDataRed'][-1]) + "," + str(data['camDataGreen'][-1]) + "," + \
                  str(data['camBPMData'][-1])
            
            f.write(row)
            f.write("\n")
    '''
    def save_to_csv(self, data):
        with io.open(self.filename, "a", newline="") as f:
            
            row = str(data['time'])       + "," + \
                  str(data['psData'])     + "," + str(data['psBPMData'])    + "," + \
                  str(data['camDataRed']) + "," + str(data['camDataGreen']) + "," + \
                  str(data['camBPMData'])
            
            f.write(row)
            f.write("\n")
            
    
    def get_cam_data_red(self):
        camData = hp.get_data(self.filename, column_name='cam_waveform_red')
        return camData
    
    def get_cam_data_green(self):
        camData = hp.get_data(self.filename, column_name='cam_waveform_green')
        return camData    
    
    def get_pulseox_data(self):
        pulseOxData = hp.get_data(self.filename, column_name='ps_waveform')
        return pulseOxData
    
    def get_time_data(self):
        timeData = hp.get_data(self.filename, column_name='time')
        return timeData
        
    def get_bpm(self):
        bpmData = hp.get_data(self.filename, column_name='ps_bpm')
        return int(bpmData.mean())
        