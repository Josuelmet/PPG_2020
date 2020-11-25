from datetime import datetime
import io

## Heartrate analysis package
import heartpy as hp
from heartpy.exceptions import BadSignalWarning



class PPG_Writer(object):
    """
    Class to save PPG data to a CSV file.
    """
    def __init__(self, csvStr=None):
        # Setup CSV File
        
        now = datetime.now()
        
        if csvStr is None:
            self.filename = 'ppg_' + now.strftime("%Y-%m-%d_%I_%M_%S")
        else:
            self.filename = csvStr
            
        self.filename = self.filename + ".csv"
        
    
    def start_writing(self):
        # Save a new CSV file to write to,
        # with the appropriate headers.
        
        headers = (u'time' + ',' + u'ps_waveform' + ',' + u'ps_bpm' + ',' + \
                   u'cam_waveform_red' + ',' + u'cam_waveform_green' + ',' + u'cam_bpm')
        
        with io.open(self.filename, 'w', newline='') as f:
            f.write(headers)
            f.write(u'\n')
    

    def save_to_csv(self, data):
        # Write the entries in data to the corresponding columns
        # in a new row of the .csv file.
        
        with io.open(self.filename, "a", newline="") as f:
            
            row = str(data['time'])       + "," + \
                  str(data['psData'])     + "," + str(data['psBPMData'])    + "," + \
                  str(data['camDataRed']) + "," + str(data['camDataGreen']) + "," + \
                  str(data['camBPMData'])
            
            f.write(row)
            f.write("\n")
            
    
    '''
    .csv file time-series column extraction functions
    '''
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
        
    '''
    .csv file BPM average extraction function
    '''
    def get_bpm(self):
        bpmData = hp.get_data(self.filename, column_name='ps_bpm')
        return int(bpmData.mean())
        