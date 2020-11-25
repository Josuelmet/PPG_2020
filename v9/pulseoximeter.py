import serial
import array

class CMS50D(object):
    #TODO: Properly decode "finger out" flag, assuming it exists
    def __init__(self, portstr):
        # timeout needs to be at least 0.017 seconds, which is (1/60) of a second.
        self.port = serial.Serial(portstr, 115200, timeout=0.017, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, xonxoff=1)
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
        
        # Instead of capturing the normal 9 bytes,
        # capture 18 bytes b/c the loop this function is called from usually
        # runs at 30Hz, which is half as fast as the pulse oximeter sends data.
        raw = self.port.read(9*2)
        #print(len(raw))
        
        if len(raw) < 9:
            # Every ~30 seconds the pulse oximeter needs to receive the handshake bytestream
            self.port.write(b'\x7d\x81\xa1\x80\x80\x80\x80\x80\x80')
            return {"spo2":0, "pulseRate":0, "pulseWaveform":0}
        
        readings["spo2"] = raw[6] & 0x7f
        readings["pulseRate"]   = raw[5] & 0x7f
        readings["pulseWaveform"] = raw[3] & 0x7f
        return readings
            

            

# Example of usage:

if __name__ == '__main__':
    
    import time
    from performancetracker import PerformanceTracker


    pulseOx=CMS50D("/dev/ttyUSB0")

    tracker = PerformanceTracker()
    tracker.reset()
    
    # 40 seconds
    t_end = time.time() + 30

    while time.time() < t_end:
        data = pulseOx.get_data()
        print(data)
        tracker.track_performance(print_period=False, print_frequency=True)

    pulseOx.close()
