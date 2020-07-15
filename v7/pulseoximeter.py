import serial
import array

class CMS50D(object):
    #TODO: Properly decode "finger out" flag, assuming it exists
    def __init__(self, portstr):
        self.port = serial.Serial(portstr, 115200, timeout=0.1, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, xonxoff=1)
        self.current_bpm = None
        self.current_spo2 = None
        self._buf = array.array('B')
        self.port.write(b'\x7d\x81\xa1\x80\x80\x80\x80\x80\x80')

    def close(self):
        self.port.close()
        
    
    '''
    Returns a dictionary with keys "SPO2", "PulseRate", and "PulseWaveform".
    '''    
    def get_data(self):
        readings = {}
        
        raw = self.port.read(9)
        if len(raw) < 9:
            return {"spo2":0, "pulseRate":0, "pulseWaveform":0}
        
        readings["spo2"] = raw[6] & 0x7f
        readings["pulseRate"]   = raw[5] & 0x7f
        readings["pulseWaveform"] = raw[3] & 0x7f
        return readings
            

            

# Example of usage:

if __name__ == '__main__':
    
    from performancetracker import PerformanceTracker


    pulseOx=CMS50D("/dev/ttyUSB0")

    tracker = PerformanceTracker()
    tracker.reset()

    for x in range (100):
        data = pulseOx.get_data()
        print(data)
        tracker.track_performance(False, True)

    pulseOx.close()
