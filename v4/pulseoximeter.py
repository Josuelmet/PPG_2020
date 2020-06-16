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
            
            
    '''
    def get_data(self):
        # read 8 bytes, put them in the array _buf.
        self._buf.frombytes(self.port.read(8))
        
        data = []
        i = 0
        state = 0
        lvl = 0
        pulse = 0
        blip = 0
        ox = 0
        while (len(self._buf) >= (5 - state)):
            b = self._buf.pop(0)
            if state == 0:
                if b & 0x80 == 0x80:
                    if (b & 0x40):
                        blip = 1
                    else:
                        blip = 0
                    state = 1
            elif state == 1:
                lvl = b
                state = 2
            elif state == 2:
                if (b & 0x40):
                    pulse = 128
                else:
                    pulse = 0
                state = 3
            elif state == 3:
                pulse += b
                state = 4
            elif state == 4:
                ox = b
                data.append((lvl,blip,pulse,ox))
                state = 0
        return data
    '''
            

# Example of usage:
'''
pulseOx=CMS50D("COM14")

for x in range (0,100):
    data=pulseOx.get_data()

    print(data)

pulseOx.close()
'''