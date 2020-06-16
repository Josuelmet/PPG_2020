# GUI and plotting tools
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui







'''
The main GUI code for the PPG.
'''
class PPG_GUI(object):
    
    
    def __init__(self, data_dict):
        
        ## Qt GUI Setup
        pg.mkQApp()
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle('Remote PPG')
        # end Qt Setup
        
        #### GUI Setup
        ## Plot for image
        '''
        Create 2-D image plot
        Fix aspect ratio
        Create a button to be used for exit function.
        Move on to the next row in the window
        '''
        self.imgPlot = self.win.addPlot(colspan=2)
        self.imgPlot.getViewBox().setAspectLocked(True)
        self.win.nextRow()
        
        ## Plot for camera intensity
        '''
        Create camera pulse and camera bpm plots
        Move on to the next row in the window
        '''
        self.camPlot = self.win.addPlot()
        self.camBPMPlot = self.win.addPlot()
        self.win.nextRow()
        
        ## Plot for pulse sensor intensity
        '''
        Create pulse sensor waveform and bpm plots.
        '''
        self.psPlot = self.win.addPlot()
        self.psBPMPlot = self.win.addPlot()
        
        # ImageItem box for displaying image data
        self.img = pg.ImageItem()
        self.imgPlot.addItem(self.img)
        self.imgPlot.getAxis('bottom').setStyle(showValues=False)
        self.imgPlot.getAxis('left').setStyle(showValues=False)
        self.imgPlot.getAxis('bottom').setPen(0,0,0)
        self.imgPlot.getAxis('left').setPen(0,0,0)
        
#        self.win.show() # Display the window
        #### end GUI Setup
        
        
        
        
        ### Initalize GUI
        '''
        Camera waveform: both axes won't show number values.
        Camera bpm: bottom axis won't show values, left axis will.
        Pulse sensor waveform: both axes won't show values.
        Pulse sensor bpm: bottom axis won't show values, left axis will.
        '''
#        self.camPlot.getAxis('bottom').setStyle(showValues=False)
#        self.camPlot.getAxis('left').setStyle(showValues=False)
        self.camPlot.setLabel('left','Cam Signal')
        
#        self.camBPMPlot.getAxis('bottom').setStyle(showValues=False)
        self.camBPMPlot.setLabel('left','Cam BPM')
        
#        self.psPlot.getAxis('bottom').setStyle(showValues=False)
#        self.psPlot.getAxis('left').setStyle(showValues=False)
        self.psPlot.setLabel('left','PS Signal')
        
#        self.psBPMPlot.getAxis('bottom').setStyle(showValues=False)
        self.psBPMPlot.setLabel('left','PS BPM')
        
        
        '''
        Create curves for each graph.
        Camera curves are yellow. Pulse curves are green.
        '''
        camPen = pg.mkPen(width=10, color='y')
        psPen  = pg.mkPen(width=10, color='g')
        
        self.camCurve    = self.camPlot.plot(    data_dict["time"], data_dict['camData'],    pen=camPen, name="Camera")
        self.camBPMCurve = self.camBPMPlot.plot( data_dict["time"], data_dict['camBPMData'], pen=camPen, name="Cam BPM")
        self.psCurve     = self.psPlot.plot(     data_dict["time"], data_dict['psData'],     pen=psPen,  name="Pulse Sensor")
        self.psBPMCurve  = self.psBPMPlot.plot(  data_dict["time"], data_dict['psBPMData'],  pen=psPen,  name="PS BPM")
        ### End GUI initialization
        
        
        # Miscellaneous variable initialization
        self.scroller = 0
        
    def start(self):
        print('showing window')
        self.win.show()
        QtGui.QApplication.instance().exec_()         
        print('finished calling exec_()')
        
        
    def update(self, image, data_dict):

        
        self.img.setImage(image, autoLevels=True)
        

    
        self.scroller += 1
        self.camCurve.setPos(self.scroller, 0)
        
        self.camCurve.setData(   data_dict['camData']   )
        self.camBPMCurve.setData(data_dict['camBPMData'])
        self.psCurve.setData(    data_dict['psData']    )
        self.psBPMCurve.setData( data_dict['psBPMData'] )

