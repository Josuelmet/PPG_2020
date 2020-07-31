__author__ = "Mayank Kumar", "Akash Kumar Maity"
__copyright__ = "Copyright 2015, Rice Scalable Health"

# Core python
import serial 
from serial import SerialException
import os, sys
import time, re, datetime
import shutil
import subprocess
from subprocess import Popen, PIPE, STDOUT 
import signal
import glob
import re
import numpy as np
# Scientific computing 
import cv2


# PyQT4 for GUI  
from PyQt5 import Qt, QtGui, QtCore
from storage_UI import Ui_MainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot #,QString 
from PyQt5.QtWidgets import (QWidget, QLabel, QMainWindow,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QPushButton, QGroupBox, QMessageBox,
                             QPlainTextEdit, QInputDialog,
                             QApplication, QLineEdit, QLCDNumber)

# multiprocessing and multi-threading 
from multiprocessing import Process, Queue, Event
from queue import Empty 



# PyDistancePPG-implemented 
from pyDistancePPG.pulse_ox import CMS50D 
from pyDistancePPG.cameraControl import cameraControl 



from storage import storage
from storage_PulseOx import storage_PulseOx

import CONFIG

from time import strftime
# Buffers
MAXFRAME = 2400
MAXSAMPLE = 90000 


frameBuffer1 = Queue(maxsize=MAXFRAME)
#frameBuffer2 = Queue(maxsize=MAXFRAME)

pulseOxBuffer = Queue(maxsize=MAXSAMPLE)
pulseOxBuffer2 = Queue(maxsize=MAXSAMPLE)
'''
if CONFIG.NUM_OX==2:
    pulseOxBuffer = Queue(maxsize=MAXSAMPLE)
    pulseOxBuffer2 = Queue(maxsize=MAXSAMPLE)
elif CONFIG.NUM_OX==1:
    pulseOxBuffer = Queue(maxsize=MAXSAMPLE)
'''

# Events (inter process communication)
startStorage = Event()
stopStorage = Event() 


# Global variables
flag_store = [False, False]
flag_stop = [False,False]
flag_setup = [False, False]
# NEw feature requests

# 3. Display time of experiment in the GUI


class MainUi(QMainWindow):
    """
    Main GUI class. Implements everything GUI related. Also, create instance of PPGProcessing and 
    featureTracking as a separate multiprocessing class. 
    """
    startSignal = pyqtSignal(object)
    stopSignal = pyqtSignal(object)
    quit_program = pyqtSignal()
    new_portstr = pyqtSignal(str)

    global flag_start
    global flag_stop


    def __init__(self):
        QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        startStorage.clear()
        stopStorage.clear()

        #Initialize Timer
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.start_time = 0
        self.ui.timer_lcd.display("%02d:%02d" % (self.start_time/60,self.start_time % 60))

        # separete threads to run frame grabber and store
        self.frameGrabber1 = flyCaptureStore(0)
        self.frameReader1 = flyCaptureRead(0)

        self.frameGrabber2 = flyCaptureStore(1)
        self.frameReader2 = flyCaptureRead(1)



        #self.frameGrabber2 = frameGrabber(frameBuffer2)

        self.cam1 = False
        self.cam2 = False
        self.cam3 = False
        self.px1 = False
        self.px2 = False

        self.p_id = None

        # Default place to dump data file.
        self.dataDump_base = os.path.join(os.getcwd(),'dump')

        if not os.path.exists(self.dataDump_base):
            os.makedirs(self.dataDump_base)

        self.webcam_folder = os.path.join(self.dataDump_base, 'Webcam')
        self.pulseOx_folder = os.path.join(self.dataDump_base, 'PulseOX')


        # Delete stray files resulting from this experiment
        shutil.rmtree('cam_flea3_0', ignore_errors=True)
        os.remove('CameraCyclesLog0.txt') if os.path.exists('CameraCyclesLog0.txt') else None
        os.remove('CameraBufferSize0.txt') if os.path.exists('CameraBufferSize0.txt') else None
        os.remove('CameraFrame0.txt') if os.path.exists('CameraFrame0.txt') else None
        os.remove('CameraTimeLog0.txt') if os.path.exists('CameraTimeLog0.txt') else None
        os.remove('Config0.txt') if os.path.exists('Config0.txt') else None
#        os.remove('Setup0.log') if os.path.exists('Setup0.log') else None
#        os.remove('FlyCap0.log') if os.path.exists('FlyCap0.log') else None

        shutil.rmtree('cam_flea3_1', ignore_errors=True)
        os.remove('CameraCyclesLog1.txt') if os.path.exists('CameraCyclesLog1.txt') else None
        os.remove('CameraBufferSize1.txt') if os.path.exists('CameraBufferSize1.txt') else None
        os.remove('CameraFrame1.txt') if os.path.exists('CameraFrame1.txt') else None
        os.remove('CameraTimeLog1.txt') if os.path.exists('CameraTimeLog1.txt') else None
        os.remove('Config1.txt') if os.path.exists('Config1.txt') else None
#        os.remove('Setup1.log') if os.path.exists('Setup1.log') else None
#        os.remove('FlyCap1.log') if os.path.exists('FlyCap1.log') else None

        if not os.path.exists(self.pulseOx_folder):
            os.makedirs(self.pulseOx_folder)


        self.frameGrabber3 = frameGrabber(frameBuffer1)
        self.frameWriter3 = storage(frameBuffer1, stopStorage, self.webcam_folder, 'webcam')

        self.pulseOxWriter1 = storage_PulseOx(pulseOxBuffer, stopStorage, self.pulseOx_folder, 'px1')
        self.pulseOxWriter2 = storage_PulseOx(pulseOxBuffer2, stopStorage, self.pulseOx_folder, 'px2')


        self.ui.push_start.clicked.connect(self.push_start_clicked)
        self.ui.push_stop.clicked.connect(self.push_stop_clicked)
        self.ui.push_setup.clicked.connect(self.push_setup_clicked)
        self.ui.push_process.clicked.connect(self.push_process_clicked)
        self.ui.cameraControlWidget[0].push_cameraSetup.clicked.connect(self.push_cameraSetup_clicked)
        self.ui.cameraControlWidget[1].push_cameraSetup.clicked.connect(self.push_cameraSetup_clicked)

        if CONFIG.WEBCAM:
            self.ui.push_inc_webcam_gain.clicked.connect(self.increase_webcam_gain)
            self.ui.push_dec_webcam_gain.clicked.connect(self.decrease_webcam_gain)
            self.ui.push_inc_webcam_exp.clicked.connect(self.increase_webcam_exposure)
            self.ui.push_dec_webcam_exp.clicked.connect(self.decrease_webcam_exposure)

        if CONFIG.PROFILE==0: # operating room profile
            self.OT_event_file = os.path.join(self.dataDump_base, 'OT_event.log')
            self.OT_event_file_handle = open(self.OT_event_file, 'w')
            self.ui.OTEventBlock.push_Event_1.clicked.connect(self.handle_OT_events)
            self.ui.OTEventBlock.push_Event_2.clicked.connect(self.handle_OT_events)
            self.ui.OTEventBlock.push_Event_3.clicked.connect(self.handle_OT_events)
            self.ui.OTEventBlock.push_Event_1.setEnabled(False)
            self.ui.OTEventBlock.push_Event_2.setEnabled(False)
            self.ui.OTEventBlock.push_Event_3.setEnabled(False)



       
        #self.connect(self.ui.toolbar.config, QtCore.SIGNAL("triggered()"), self.ui.config_form.show)
        #self.connect(self.ui.config_form, QtCore.SIGNAL("new_config"), self.update_config)
        #self.resultTimer = QtCore.QTimer(self)
        #self.resultTimer.timeout.connect(self.show_result)
        self.statusBar()
        #self.addToolBar(self.ui.toolbar)
        
    def start_timer(self):
        # Start timer and update display
        self.now = 0
        self.timer.timeout.connect(self.tick_timer)
        self.timer.start()
        self.update_timer()

    def update_timer(self):
        self.runtime = "%02d:%02d" % (self.now/60,self.now % 60)
        self.ui.timer_lcd.display(self.runtime)

    def tick_timer(self):
        self.now += 1
        self.update_timer()

    def stop_timer(self):
        self.timer.stop()

    def push_setup_clicked(self):
        global flag_setup
        if(self.cam1):
            flag_setup[0] = True
        if(self.cam2):
            flag_setup[1]= True
        if (self.cam3):
            self.frameGrabber3.cc.setManualExposure()
            self.frameGrabber3.cc.increaseGain()

    def push_process_clicked(self):
        if self.p_id is None: # No experiment started
            # ask user for patient ID to process
            p_id, ok = QInputDialog.getText(self, 'Experiment ID',
                                                  'Please enter Experiment Unique identifier (EID)')
            if ok:
                p_id = str(p_id)
            else:
                pass
        else:
            p_id = self.p_id


        pid_folder = os.path.join(self.dataDump_base, p_id)



        if os.path.exists(pid_folder):
            self.ui.push_process.setEnabled(False)
            # FIXME: Assuming only one camera for processing
            cam_folder1 = os.path.join(pid_folder, 'cam_flea3_0')
            numFrames = len(os.listdir(cam_folder1))
            numFrames = numFrames - (numFrames%900)
            matlab_process = Popen(['sudo','-u', 'ashoklab', 'matlab', '-nodesktop', '-nosplash', '-r', "try, setup_pulseCam_recorder('"+p_id+"'," +str(numFrames)+", 1); catch, disp('Program failed'), end; try, pulseCam_recorder_start('" + p_id + "'); catch, disp('Program failed'), end, quit; "], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #stdout, stderr = matlab_process1.communicate()
            #print(stdout)
            #print(stderr)
            #matlab_process2 = Popen(['sudo', '-u', 'ashoklab', 'matlab', '-nodesktop', '-nosplash', '-r',
            #                 "try, pulseCam_recorder_start('" + p_id + "'); catch, disp('Program failed'), end, quit"], stdout=subprocess.PIPE,
            #                stderr=subprocess.PIPE)



            def check_condition():
                if matlab_process.poll() is None:
                    self.show_message(' <b> Wait: </b> processing the data ...')
                    QtCore.QTimer.singleShot(30000, check_condition)
                else:
                    self.show_message(' <b> Done processing ! </b>')
                    self.ui.push_process.setEnabled(True)

            self.show_message(' <b> Wait: </b> processing the data ')

            QtCore.QTimer.singleShot(30000,check_condition)


            '''
            while matlab_process2.poll() is None:
                time.sleep(30)
                counter += 1.0
                self.show_message(' <br> Wait: </br> processing the data ... please wait ... '+str(counter/2.0)+ 'min passed!')
            else:
                self.ui.push_process.setEnabled(True)
            '''



        else:
            self.show_error('Experiment ID do not exist')
            self.ui.push_process.setEnabled(True)





            #setup_pulseCam_recorder('Mayank_hand_ice', 1800, 1);







    def push_start_clicked(self):
        # Set camera parameters as required.
        global flag_store

        if self.px1:
            self.pulseOxWriter1.start()
        if self.px2:
            self.pulseOxWriter2.start()

        if self.cam1:
            self.frameGrabber1.camera_run.send_signal(signal.SIGUSR1)
            flag_store[0] = True
        if self.cam2:
            self.frameGrabber2.camera_run.send_signal(signal.SIGUSR1)
            flag_store[1] = True
        if self.cam3:
            if not os.path.exists(self.webcam_folder):
                os.makedirs(self.webcam_folder)

            self.frameGrabber3.cc.setManualExposure()
            self.frameWriter3.start()

        # increase camera Gain 
        #self.frameGrabber.cc.increaseGain()
        #self.frameGrabber.cc.increaseGain()

        # start saving frames from flea3Z


        #currentTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')





        # update config for the pulse oximeter
        #self.update_config()


        # start storing frames from the camera 
        stopStorage.clear() 

        startStorage.set()
        self.startSignal.emit(None) 

        self.ui.push_start.setEnabled(False)
        self.ui.push_setup.setEnabled(False)
        self.ui.push_stop.setEnabled(True)

        if CONFIG.PROFILE==0:
            self.ui.OTEventBlock.push_Event_1.setEnabled(True)
            self.ui.OTEventBlock.push_Event_2.setEnabled(True)
            self.ui.OTEventBlock.push_Event_3.setEnabled(True)


        self.show_message(' Started data recording ... ')
        #if not self.cam1 and not self.cam2:
            # raise error
            #self.show_error("No camera Selected, can't start. Restart program, and choose appropriate camera")
            


        #self.resultTimer.start(30)


    def push_stop_clicked(self):

        # stop storing data from pulse-ox 
        self.stopSignal.emit(None)

        # stop camera-frame storage.
        startStorage.clear()


        # stop PulseOx1 and PulseOx2 (if available)
        stopStorage.set()
        self.show_message(' <b> Stopped data recording </b>')
        
        # Revert camera to original settings.
        if self.cam3:
            self.frameGrabber3.cc.setAutoExpoure()

        if self.cam1:
            self.frameGrabber1.camera_run.send_signal(signal.SIGUSR2)
            
        if self.cam2:
            self.frameGrabber2.camera_run.send_signal(signal.SIGUSR2)

        # wait for the frames to be written to the disk
        if self.cam1 or self.cam2:
            global frame_stop
            while ((self.cam1 and flag_stop[0] == False) or (self.cam2 and flag_stop[1] == False)):
                self.show_message('Writing data to the disk ... wait ')
                time.sleep(5)
            else:
                self.show_info('Done writing data ! ')
                self.show_message('Done writing data ! ')

                


        #self.p.join()

        self.ui.push_start.setEnabled(False)
        self.ui.push_stop.setEnabled(False)
        self.ui.push_setup.setEnabled(False)


        if CONFIG.PROFILE:
            # disable the OT buttons
            self.ui.OTEventBlock.push_Event_1.setEnabled(False)
            self.ui.OTEventBlock.push_Event_2.setEnabled(False)
            self.ui.OTEventBlock.push_Event_3.setEnabled(False)
            self.OT_event_file_handle.close()


        # wait for a second
        #time.sleep(1)
        
        #self.resultTimer.stop() 

        #print "Experiment finished, now flusing ,,, "


        QtCore.QTimer.singleShot(1000,self.flush)


        # write the messages in the window to a file
        with open("window.log", 'w') as f:
            f.write(self.ui.plain_instruction.toPlainText())
        self.get_pid()

        # Get patient ID and then move data to specific folder.

    def get_pid(self):
        print('inside get_pid')
        cam_folder1 = os.path.join(os.getcwd(), 'cam_flea3_0')
        cam_folder2 = os.path.join(os.getcwd(), 'cam_flea3_1')

        if self.cam1:

            # Delete frames written before START is pressed and renaming other files
            with open('CameraFrame0.txt', 'r') as f:
                frame0 = f.readline()
            [int(s) for s in frame0.split() if s.isdigit()]
            store_cnt = 0

            filenames = sorted(glob.glob(cam_folder1 + '/*.pgm'), key=os.path.getmtime)  # assuming pgm images


            for image_cnt in range(0, len(filenames)):
                filename = filenames[image_cnt]
                [int(count) for count in os.path.split(filename)[1][:-4].split('-') if count.isdigit()]
                #print "count is" +str(count)
                #print "s is" + str(s)

                if (int(count) < int(s)):
                    os.remove(filename)
                else:
                    filestore = cam_folder1 + '/Frame' + str(store_cnt).zfill(5) + '.pgm'
                    os.rename(filename, filestore)
                    store_cnt += 1

        if self.cam2:

            # Delete frames written before START is pressed and renaming other files
            with open('CameraFrame1.txt', 'r') as f:
                frame0 = f.readline()
            [int(s) for s in frame0.split() if s.isdigit()]
            store_cnt = 0

            filename = sorted(glob.glob(cam_folder2 + '/*.pgm'), key=os.path.getmtime)  # assuming pgm images
            for image_cnt in range(0, len(filename)):
                if (image_cnt < int(s)):
                    os.remove(filename[image_cnt])
                else:
                    filestore = cam_folder2 + '/Frame' + str(store_cnt).zfill(5) + '.pgm'
                    os.rename(filename[image_cnt], filestore)
                    store_cnt += 1




        done = False
        while not done:
            p_id, ok = QInputDialog.getText(self, 'Experiment ID',
                                                  'Please enter Experiment Unique identifier (EID)')

            p_id = str(p_id)
            self.p_id = p_id
            if ok:
                pid_folder = os.path.join(self.dataDump_base, p_id)
                if os.path.exists(pid_folder):
                    self.show_error('Experiment name already used, try something new')
                    done = False
                else:
                    os.makedirs(pid_folder)
                    shutil.move("window.log",pid_folder)
                    if (self.cam1):
                        self.show_info('Moving frames for camera 1 to folder')
                        shutil.move(cam_folder1, pid_folder)
                        shutil.move("CameraTimeLog0.txt", pid_folder)
                        shutil.move("CameraFrame0.txt", pid_folder)
                        shutil.move("CameraBufferSize0.txt", pid_folder)
                        shutil.move("CameraCyclesLog0.txt", pid_folder)
                        #shutil.move("Setup0.log", pid_folder)
                        shutil.move("Config0.txt", pid_folder)
                        #shutil.move("FlyCap0.log", pid_folder)
                        shutil.move("CameraInfo0.log", pid_folder)

                    if (self.cam2):
                        self.show_info('Moving frames for camera 2 to folder')
                        shutil.move(cam_folder2, pid_folder)
                        shutil.move("CameraTimeLog1.txt", pid_folder)
                        shutil.move("CameraFrame1.txt", pid_folder)
                        shutil.move("CameraBufferSize1.txt", pid_folder)
                        shutil.move("CameraCyclesLog1.txt", pid_folder)
                        #shutil.move("Setup1.log", pid_folder)
                        shutil.move("Config1.txt", pid_folder)
                        #shutil.move("FlyCap1.log", pid_folder)
                        shutil.move("CameraInfo1.log", pid_folder)

                    if (self.cam3):
                        shutil.move(self.webcam_folder, pid_folder)

                    # move the pulse-oximeter data
                    shutil.move(self.pulseOx_folder, pid_folder)

                    # move OT Events
                    if CONFIG.PROFILE==0:
                        shutil.move(self.OT_event_file, pid_folder)
                    self.show_message('Done!!')
                    done = True

    def flush(self):
        while not frameBuffer1.empty():
            try: 
                frameBuffer1.get(False)
            except Empty:
                    continue

        '''
        while not frameBuffer2.empty():
            try:
                frameBuffer2.get(False)
            except Empty:
                continue
        '''

        while not pulseOxBuffer.empty():
            try: 
                pulseOxBuffer.get(False)
            except Empty:
                continue

    def handle_OT_events(self):
        #print('Inside the OT Event handle! ')
        sender = self.sender()
        text = self.sender().objectName() + ' Was pressed on ' + self.runtime + ' System Time = ' + str(
                datetime.datetime.now()) + '\n'

        self.OT_event_file_handle.write(text)

        self.show_message(text) # Redundancy

        self.sender().setEnabled(False)



    def read_camera_config(self, cameraID):
        filename = 'Config' + str(cameraID) + '.txt'
        with open(filename, "r") as setup:
            lines = setup.readlines()
            gain = float(lines[0].strip())
            exposure = float(lines[1].strip())
            FPS = float(lines[2].strip())
            binning = int(lines[3].strip())
            offsetX = int(lines[4].strip())
            offsetY = int(lines[5].strip())
            width = int(lines[6].strip())
            height = int(lines[7].strip())

            window.ui.cameraControlWidget[cameraID].gain_value.setText(str(gain))
            window.ui.cameraControlWidget[cameraID].exposure_value.setText(str(exposure))
            window.ui.cameraControlWidget[cameraID].FPS_value.setText(str(FPS))
            window.ui.cameraControlWidget[cameraID].Binning_value.setText(str(binning))
            window.ui.cameraControlWidget[cameraID].offsetX_value.setText(str(offsetX))
            window.ui.cameraControlWidget[cameraID].offsetY_value.setText(str(offsetY))
            window.ui.cameraControlWidget[cameraID].width_value.setText(str(width))
            window.ui.cameraControlWidget[cameraID].height_value.setText(str(height))

    def push_cameraSetup_clicked(self):
        sending_button = self.sender()
        sender_CamID = int(str(sending_button.objectName()))

        filename = 'Config' + str(sender_CamID) + '.txt'

        gain = self.ui.cameraControlWidget[sender_CamID].gain_value.text()
        exposure = self.ui.cameraControlWidget[sender_CamID].exposure_value.text()
        FPS = self.ui.cameraControlWidget[sender_CamID].FPS_value.text()
        binning = self.ui.cameraControlWidget[sender_CamID].Binning_value.text()
        offsetX = self.ui.cameraControlWidget[sender_CamID].offsetX_value.text()
        offsetY = self.ui.cameraControlWidget[sender_CamID].offsetY_value.text()
        width = self.ui.cameraControlWidget[sender_CamID].width_value.text()
        height = self.ui.cameraControlWidget[sender_CamID].height_value.text()

        with open(filename, "w") as setup:
            setup.write(gain+'\n')
            setup.write(exposure+'\n')
            setup.write(FPS+'\n')
            setup.write(binning+'\n')
            setup.write(offsetX+'\n')
            setup.write(offsetY+'\n')
            setup.write(width+'\n')
            setup.write(height+'\n')

        outfiles = open('Setup'+str(sender_CamID)+'.log', 'w')
        p = subprocess.Popen(["./Setup", str(sender_CamID)], stdout=outfiles)
        p.communicate()
        self.show_message("Set Exposure to = "+str(exposure)+"ms, "+"Set Gain to "+str(gain))




    def show_frame1(self,frame):

        height, width = frame.shape[:2] 
        pixmap=QPixmap.fromImage(QImage(frame.tostring(), width, height, QImage.Format_RGB888))
        self.ui.webcam1.setPixmap(pixmap)

    def show_frame2(self,frame):


        # This maps the openCV image (numpy) into pixmap
        height, width = frame.shape[:2] 
        pixmap=QPixmap.fromImage(QImage(frame.tostring(), width, height, QImage.Format_RGB888))
        self.ui.webcam2.setPixmap(pixmap)

    def show_frame_webcam(self,frame):
        
        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2BGRA)
        # This maps the openCV image (numpy) into pixmap 
        
        pixmap=QPixmap.fromImage(QImage(frame.tostring(), 640, 480, QImage.Format_ARGB32))
        self.ui.webcam1.setPixmap(pixmap)
#        self.ui.webcam2.setPixmap(pixmap)

    def increase_webcam_gain(self):
        if self.cam3:
            self.frameGrabber3.cc.setManualExposure()
            retVal = self.frameGrabber3.cc.increaseGain()
            if retVal is not None:
                (currentVal, newVal) = retVal
                self.show_message('Increased Gain from ' + str(currentVal) +' to '+ str(newVal))
            else:
                self.show_message("Can't increase Gain, Max reached")

    def decrease_webcam_gain(self):
        if self.cam3:
            self.frameGrabber3.cc.setManualExposure()
            retVal = self.frameGrabber3.cc.decreaseGain()
            if retVal is not None:
                (currentVal, newVal) = retVal
                self.show_message('Decreased Gain from ' + str(currentVal) +' to '+str(newVal))
            else:
                self.show_message("Can't reduce gain, Minimum reached")


    def increase_webcam_exposure(self):
        if self.cam3:
            self.frameGrabber3.cc.setManualExposure()
            retVal = self.frameGrabber3.cc.increaseExposure()
            if retVal is not None:
                (currentVal, newVal) = retVal
                self.show_message('Increased exposure time from ' + str(currentVal/10.0) +' ms to '+ str(newVal/10.0) +' ms')
            else:
                self.show_message("Can't increase exposure, Max reached")



    def decrease_webcam_exposure(self):
        if self.cam3:
            self.frameGrabber3.cc.setManualExposure()
            retVal = self.frameGrabber3.cc.decreaseExposure()
            if retVal is not None:
                (currentVal, newVal) = retVal
                self.show_message('Decreased Exposure time from ' + str(currentVal/10.0)  +' ms to '+str(newVal/10.0)+' ms')
            else:
                self.show_message("Can't reduce Exposure, minimum reached")



    def update_stats(self, hr, ox):
        #self.display_form.ox_label.setText(str(ox))
        self.ui.pulseOx.hr_label.setText(str(hr))

    def update_plot(self, newdata):
        self.ui.pulseOx.plot.add_data(newdata)


    def refresh(self):
        self.ui.pulseOx.blinker.update()
        self.ui.pulseOx.plot.replot()
    
    def blink(self):
        self.ui.pulseOx.blinker.ping()

    def update_stats2(self, hr, ox):
        # self.display_form.ox_label.setText(str(ox))
        self.ui.pulseOx2.hr_label.setText(str(hr))

    def update_plot2(self, newdata):
        self.ui.pulseOx2.plot.add_data(newdata)

    def refresh2(self):
        self.ui.pulseOx2.blinker.update()
        self.ui.pulseOx2.plot.replot()

    def blink2(self):
        self.ui.pulseOx2.blinker.ping()

    #def show_message(self, msg):
    #    self.statusBar().showMessage(msg)

    def show_message(self,input_instruction):

        currentTime = datetime.datetime.now().strftime('%H-%M-%S')
        currentTime = '<i>' + currentTime + "- </i>"
        msg = currentTime + input_instruction + "<br/>"
        self.ui.plain_instruction.appendHtml(msg)

    def show_info(self, msg):
        QMessageBox.information(self, "Wait!!", msg)

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def update_config(self):
        self.new_portstr.emit(self.ui.config_form.settings["port"])
#        self.emit(QtCore.SIGNAL("new_portstr"), self.ui.config_form.settings["port"])
        print( self.ui.config_form.settings['port'] )

    def closeEvent(self,Event):

        print( "Closing down application ... " )


        if self.cam1:
            self.frameGrabber1.stopCamera = True
            # disconnect the camera if not already disconnected.
            #try:
            poll = self.frameGrabber1.camera_run.poll()

            if poll is None:
                #process is still running
                self.frameGrabber1.camera_run.send_signal(signal.SIGUSR2)

            # FIXME: Add a sleep for 0.5 sec here

            self.frameGrabber1.quit()
            self.frameReader1.quit()
            #except:
            #    pass
        if self.cam2:
            self.frameGrabber2.stopCamera = True
            # disconnect the camera if not already disconnected.

            poll  = self.frameGrabber2.camera_run.poll()
            if poll is None:
                # process is still running
                self.frameGrabber2.camera_run.send_signal(signal.SIGUSR2)




            # FIXME: Add a sleep for 0.5 sec here

            self.frameGrabber2.quit()
            self.frameReader2.quit()
            #xcept:
            #   pass
        if self.cam3:
            self.frameGrabber3.stopCamera = True

        # write down the instruction logs


        self.quit_program.emit()
#        self.emit(QtCore.SIGNAL("quit"))
        
        time.sleep(1)

        super(MainUi, self).closeEvent(Event)


class flyCaptureStore(QtCore.QThread):
    """
    This class runs the flyCapture to capture frames from PointGrey Camera and store it on hard drive
    """
    newConfigSignal = pyqtSignal(object)
    def __init__(self, cameraID):
        QtCore.QThread.__init__(self)
        self.cameraID = cameraID
        self.stopCamera = False
        self.cap = None

        # Directing output to a log file
        self.info_log = open('CameraInfo'+str(cameraID)+'.log','w')
        self.setup_log = open('Setup'+str(cameraID)+'.log','w')
        self.running_log = open('FlyCap'+str(cameraID)+'.log','w')




        #self.frameCounter=0

    def __del__(self):
        self.wait()

    def run(self):

        # run the CameraInfo
        self.camera_info = subprocess.Popen(["./CameraInfo", str(self.cameraID)], stdout=self.info_log)
        self.camera_info.communicate()

        # read the CameraInfo file to decide which Config file to use
        self.info_log = open('CameraInfo' + str(self.cameraID) + '.log', 'r')

        GS_FLAG = False
        FLEA_FLAG = False
        for line in self.info_log:
            if 'Grasshopper3' in line:
                GS_FLAG = True
            if 'Flea3' in line:
                FLEA_FLAG = True

        if GS_FLAG:
            shutil.copy('Config_GS3.txt', 'Config'+str(self.cameraID)+'.txt')

        if FLEA_FLAG:
            shutil.copy('Config_flea3.txt', 'Config' + str(self.cameraID) + '.txt')

        # emit signal so that the GUI can read the Config files
        self.newConfigSignal.emit(self.cameraID)



        # run the camera setup using the correct Config file
        self.camera_setup = subprocess.Popen(["./Setup", str(self.cameraID)], stdout=self.setup_log)
        self.camera_setup.communicate()

        # now run the camera
        self.camera_run = subprocess.Popen(["./FlyCap", str(self.cameraID)], stdout=self.running_log)
        self.camera_run.communicate()


        # The process will end when we send SIGUSER2 which will be done once the user press STOP button.

        # wait for the process to end

        global flag_stop

        flag_stop[self.cameraID] = True


class flyCaptureRead(QtCore.QThread):
    """
    This class reads stored frame from the hard drive
    """
    newFrameSignal = pyqtSignal(object)

    def __init__(self, cameraID):
        QtCore.QThread.__init__(self)
        self.cameraID = cameraID
        # self.frameCounter=0
        #self.mask = np.full((512, 640), True, dtype=bool)

    def __del__(self):
        self.wait()

    # read every 4th image and emits it for display
    def run(self):
        global flag_setup
        global flag_stop
        global flag_store

        image_cnt = 0
        while (True):
            filename = 'cam_flea3_'+str(self.cameraID)+'/frame-' + str(image_cnt) + '.pgm'

            if os.path.isfile(filename):
                # Step 1: check if the image count is more than the latest frame written. If so, wait for some time
                wait = True
                while wait:
                    # FIXME: More efficient implementation is feasible. Think of just asking for the latest file from the OS
                    list_of_files = glob.glob('cam_flea3_'+str(self.cameraID)+'/frame-*.pgm')
                    # if list_of_files is empty, all frames have been read and renamed, check for flag_stop and exit the program
                    if list_of_files:
                        latest_file = max(list_of_files, key=os.path.getctime)
                        # extract the frame number of the latest file written by the PointGrey camera
                        num = re.findall("\d+", latest_file)
                        # wait for some time otherwise it will display half-written frames
                        # if flag_stop = true, read the remaining frames and exit, else wait for some time to display the next frame
                        if (image_cnt >= (int(num[2]) - 1) and flag_stop[self.cameraID] == False):
                            self.msleep(33)
                            wait = True
                        else:
                            wait = False
                    else:
                        wait = False

                    # FIXME: See this error
                    # RESOLVED:
                        '''
                         Traceback (most recent call last):
                          File "main.py", line 622, in run
                            num = re.findall("\d+", latest_file)
                        AttributeError: 'NoneType' object has no attribute 'findall'
                        '''

                # Step 2: read every Nth frame and display
                if ((flag_store[self.cameraID] and image_cnt % 4 == 0) or not flag_store[self.cameraID]):
                    frame = cv2.imread(filename, -1)
                    frame_color = cv2.cvtColor(frame, cv2.COLOR_BAYER_BG2BGR)
                    frame_color_r2 = frame_color[::2, ::2, :]
                    if frame_color_r2.shape[0] > 800: # temporary for grasshopper
                        frame_color_r2 = frame_color_r2[::2, ::2, :]
                        

                    # send frame for display to the GUI
                    self.newFrameSignal.emit(frame_color_r2)

                # Step 3. Delete the frame if flag_store is false
                # Stage 1: User did not press start
                #       Flag_store = False, Flag_stop is False  --- condition True to remove files
                # Stage 2: User press Start
                #       Flag_store = True, Flag_stop is False ---- Files not deleted any more
                # Stage 3: User press Stop and before the C++ program clears the buffer
                #       Flag_store = True, Flag_stop is False ---- Files not deleted any more
                # Stage 4: All Done
                #       Flag_store = True, Flag_stop is True ---- Files not deleted any more...
                if not flag_store[self.cameraID] and not flag_stop[self.cameraID]:
                    os.remove(filename)

                image_cnt+=1
            else:
                self.msleep(33)

            # Step 3: Display the buffer size on terminal for debug

            if (image_cnt % 300 == 0):
                try:
                    file = open("CameraBufferSize"+str(self.cameraID)+".txt", 'r')
                    lines = file.read().splitlines()
                    last_line = lines[-1]
                    print('PointGrey'+str(self.cameraID)+' Buffer Size: %s' % last_line)
                except:
                    pass

            # FIXME: This process will terminate before the display of all frames are done.
            if flag_stop[self.cameraID]:
                self.terminate()
                return




class frameGrabber(QtCore.QThread):
    """
    This class implements the camera aquisition logic (From webcam)
    """
    newFrameSignal = pyqtSignal(object)
    def __init__(self, frameBuffer, cameraID=0):
        QtCore.QThread.__init__(self)
        self.cameraID = cameraID 
        self.stopCamera = False
        self.frameBuffer = frameBuffer 
        self.cap = None 
        #self.frameCounter=0 

    def __del__(self):
        self.wait() 

    def run(self):
        self.cap = cv2.VideoCapture(self.cameraID)
        self.cc = cameraControl(self.cameraID)

        if not self.cap.isOpened():
            print( 'camera cannot be opened, check webcam' )
            return 

        while not self.stopCamera:
            ret, frame = self.cap.read()
            currentTime = time.time() 
            self.newFrameSignal.emit(frame)
            if startStorage.is_set():
                #self.frameCounter+=1
                try:
                    self.frameBuffer.put((currentTime,frame),False)
                except:
                    # FIXME: silently dropping frames if frameBuffer Full
                    print( "Dropping frame as frameBuffer is full" )
                    continue

        print( "Closing camera ... terminating" )
        self.cap.release()
        self.terminate() 
        return


class PulseOX(Qt.QObject):
    """
    This class is used to control the pulse oximeter attached to the computer for ground truth measurement.
    """
    
    error = pyqtSignal(str)
    new_status = pyqtSignal(str)
    running = pyqtSignal(bool)
    
    new_stats = pyqtSignal(int, int)
    new_plotdata = pyqtSignal(int)
    tick = pyqtSignal()
    heartbeat = pyqtSignal()
    
    
    interval = 0.1 # ms, how often to read from pulse-oximeter. 
    def __init__(self, *args):
        Qt.QObject.__init__(self, *args)
        self.pulseOxAvailable = False
        self._hr = None
        self._ox = None
        self._podev = None
        self._beat = False
        self._pasttime = 0.0 
        self.timer_id = None
        self.portstr = None
        self.pulseOxBuffer = None
        #self.numSample = 0 

    
    def set_portstr(self, path):
        self.portstr = path
    
    def _start_failed(self,msg):
        self.error.emit(msg)
        self.new_status.emit("Failed to start.")
        self.running.emit(False)
#        self.emit(QtCore.SIGNAL("error"),msg)
#        self.emit(QtCore.SIGNAL("new_status"), "Failed to start.")
#        self.emit(QtCore.SIGNAL("running"), False)
    
    def start(self):
        print( "Starting pulseOx" )
        if self.portstr in (None,""):
            #pass
            return self._start_failed("No pulse-oximeter connected!")
        if self._podev is not None:
            self.stop()
        try:
            self._podev = CMS50D(self.portstr)
        except SerialException as ex:
            return self._start_failed("Couldn't connect to device:\n" + str(ex))

        self.new_status.emit("Running.")
        self.running.emit(True)
#        self.emit(QtCore.SIGNAL("new_status"), "Running.")
#        self.emit(QtCore.SIGNAL("running"), True)
        
        # this is the event ... 
        self.timer_id = self.startTimer(self.interval)

    def stop(self):
        print( "Stopping pulseOx" )
        if self._podev != None:
            self._podev.close()
            self._podev = None
        if self.timer_id:
            self.killTimer(self.timer_id)
        

        self.new_status.emit("Stopped.")
        self.running.emit(False)
#        self.emit(QtCore.SIGNAL("new_status"), "Stopped.")
#        self.emit(QtCore.SIGNAL("running"), False)
  


    # called every tick 
    def timerEvent(self, foo):
        data = None 
        try:
            
            data = self._podev.get_data()
        except Exception as ex:
            self.stop()
            # self.emit(QtCore.SIGNAL("error"),"Error reading data:\n" + str(ex))
            self.new_status.emit("Cannot read pulse-ox.")
#            self.emit(QtCore.SIGNAL("new_status"), "Cannot read pulse-ox.")
            return
        if data:
            currentTime = time.time() 

            #print currentTime - self._pasttime 
            #self._pasttime = currentTime 
            lvls, beats = zip(*data)[0:2]
            #hrs,oxs = zip(*data)[2:4]

            
            
            #self.numSample+=1 
            self.pulseOxBuffer.put((currentTime,lvls))

            if self._beat:
                self._beat = False
            else:
                if 1 in beats:
                    self._beat = True
                    self.heartbeat.emit()
#                    self.emit(QtCore.SIGNAL("heartbeat"))
            hr, ox = data[-1][2:4]
            if (hr != self._hr) or (ox != self._ox):
                self._hr = hr
                self._ox = ox
                self.new_stats.emit(hr, ox)
#                self.emit(QtCore.SIGNAL("new_stats"), hr, ox)
            self.new_plotdata.emit(lvls)
            self.tick.emit()
#            self.emit(QtCore.SIGNAL("new_plotdata"), lvls)
#            self.emit(QtCore.SIGNAL("tick"))




    def quit(self):
        #pass 
        self.stop()





if __name__=='__main__': 
    
    # setup the GUI 
    app=QApplication(sys.argv)
    window=MainUi()
    window.show()
    window.showMaximized()

    #plt.ion() 
    #plt.show() 

    
    # Get the camera Available in system.
    def get_trailing_number(s):
        m = re.search(r'\d+$', s)
        return int(m.group()) if m else None

    # get all the webcam paths in the system

    if CONFIG.PROFILE: # if not surgery room
        if sys.platform.startswith('lin'):
            DEVPATH = '/dev/'
            cameras = [f for f in os.listdir(DEVPATH) if f.startswith('vid')]
            cameraIDs = map(get_trailing_number,cameras)

    # get all the Point-grey paths
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    cameras = []
    cameraIDs = []
    id = 0
    for i in df.decode().split('\n'):
        if i:
                info = device_re.match(i)
                if info:
                        dinfo = info.groupdict()
                        dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                        devices.append(dinfo)
                        if(dinfo['tag'].startswith('Point Grey')):
                            cameras.append('PointGrey%d'%id)
                            cameraIDs.append(id)
                            id += 1


#    if not cameras:
#        print("No camera detected ... please plug the camera ... and restart")
#        sys.exit(-1)
#    else:
#        print (cameras)
#        cameras.append('None')

    # FIXME: write equivalent code for OSx

    if CONFIG.PROFILE==0: # if surgery room, don't given any option and detect the first camera
        window.cam3 = True
        # start() is a function in the QThread class.
        # By default it calls the run() function.
        window.frameGrabber3.start()
        
#        window.cam1 = True
#        window.frameGrabber1.start()
#        window.frameReader1.start()
    else:

        selectedCamera1, ok1 = QInputDialog.getItem(window, 'Select Camera',
            'Please Select first camera',list(reversed(cameras)))

        selectedCamera2, ok2 = QInputDialog.getItem(window, 'Select Camera',
            'Please Select second camera',list(reversed(cameras)))


        if ok1 and selectedCamera1!='None':
            if selectedCamera1 == 'PointGrey0':
                # Camera 1 selected
                window.frameGrabber1.start()
                window.frameReader1.start()
                window.cam1 =True
            elif selectedCamera1 =='PointGrey1':
                window.frameGrabber2.start()
                window.frameReader2.start()
                window.cam2 = True
            else:
                window.frameGrabber3.cameraID = cameraIDs[0]
                window.frameGrabber3.start()
                window.cam3 = True




        if ok2 and selectedCamera2!='None':
            if selectedCamera2 == 'PointGrey0':
                # Camera 1 selected
                window.frameGrabber1.start()
                window.frameReader1.start()
                window.cam1 =True
            elif selectedCamera2 =='PointGrey1':
                window.frameGrabber2.start()
                window.frameReader2.start()
                window.cam2 = True
            else:
                window.frameGrabber3.cameraID = cameraIDs[0]
                window.frameGrabber3.start()
                window.cam3 = True


    
    '''
    if window.cam1: # PointGrey0 selected



    if window.cam2:
        filename = 'Config' + str(1) + '.txt'
        with open(filename, "r") as setup:
            lines = setup.readlines()
            gain = float(lines[0].strip())
            exposure = float(lines[1].strip())
            FPS = float(lines[2].strip())
            binning = int(lines[3].strip())
            offsetX = int(lines[4].strip())
            offsetY = int(lines[5].strip())
            width = int(lines[6].strip())
            height = int(lines[7].strip())

            window.ui.cameraControlWidget2.gain_value.setText(str(gain))
            window.ui.cameraControlWidget2.exposure_value.setText(str(exposure))
            window.ui.cameraControlWidget2.FPS_value.setText(str(FPS))
            window.ui.cameraControlWidget2.Binning_value.setText(str(binning))
            window.ui.cameraControlWidget2.offsetX_value.setText(str(offsetX))
            window.ui.cameraControlWidget2.offsetY_value.setText(str(offsetY))
            window.ui.cameraControlWidget2.width_value.setText(str(width))
            window.ui.cameraControlWidget2.height_value.setText(str(height))
    '''





    # get all the pulse oximeters


    DEVPATH = '/dev/'
    tty_pfxs = "ttyUSB"
    pulse_ox = [f for f in os.listdir(DEVPATH) if f.startswith(tty_pfxs)]

    pulse_ox_path = [DEVPATH + px for px in pulse_ox]

    #selectedCamera, ok =
    if pulse_ox:
        window.px1 = True
        px1 = PulseOX()
        px1.pulseOxAvailable = True
        px1.portstr=pulse_ox_path[0]
        px1.pulseOxBuffer = pulseOxBuffer
        print( px1.portstr )

        # signals originating in pulse ox
        px1.new_stats.connect(window.update_stats)
        px1.new_status.connect(window.show_message)
        px1.heartbeat.connect(window.blink)
        px1.new_plotdata.connect(window.update_plot)
        px1.tick.connect(window.refresh)
        px1.error.connect(window.show_error)
#        app.connect(px1, QtCore.SIGNAL("new_stats"), window.update_stats)
#        app.connect(px1, QtCore.SIGNAL("new_status"), window.show_message)
#        app.connect(px1, QtCore.SIGNAL("heartbeat"), window.blink)
#        app.connect(px1, QtCore.SIGNAL("new_plotdata"), window.update_plot)
#        app.connect(px1, QtCore.SIGNAL("tick"), window.refresh)
#        app.connect(px1, QtCore.SIGNAL("error"), window.show_error)

        # signals originating in windows
        window.quit_program.connect(px1.quit)
        window.new_portstr.connect(px1.set_portstr)
#        app.connect(window, QtCore.SIGNAL("quit"), px1.quit)
#        app.connect(window, QtCore.SIGNAL("new_portstr"), px1.set_portstr)

        window.startSignal.connect(px1.start)
        window.stopSignal.connect(px1.stop)

        if len(pulse_ox)>1:
            # second pulse-ox present
            window.px2 = True
            print('Detected second pulse oximeter')
            px2 = PulseOX()
            px2.pulseOxAvailable = True
            px2.portstr=pulse_ox_path[1]
            px2.pulseOxBuffer = pulseOxBuffer2
            print( px2.portstr )


            # signals originating in pulse ox
            px1.new_stats.connect(window.update_stats2)
            px1.new_status.connect(window.show_message)
            px1.heartbeat.connect(window.blink2)
            px1.new_plotdata.connect(window.update_plot2)
            px1.tick.connect(window.refresh2)
            px1.error.connect(window.show_error)
#            app.connect(px2, QtCore.SIGNAL("new_stats"), window.update_stats2)
#            app.connect(px2, QtCore.SIGNAL("heartbeat"), window.blink2)
#            app.connect(px2, QtCore.SIGNAL("new_plotdata"), window.update_plot2)
#            app.connect(px2, QtCore.SIGNAL("tick"), window.refresh2)
#            app.connect(px2, QtCore.SIGNAL("error"), window.show_error)
#            app.connect(px2, QtCore.SIGNAL("new_status"), window.show_message)

            # signals originating in windows
            window.quit_program.connect(px2.quit)
            window.new_portstr.connect(px2.set_portstr)
#            app.connect(window, QtCore.SIGNAL("quit"), px2.quit)
#            app.connect(window, QtCore.SIGNAL("new_portstr"), px2.set_portstr)

            window.startSignal.connect(px2.start)
            window.stopSignal.connect(px2.stop)
    else:
        print('Pulse-oximeter not detected, please plug the pulse-ox and restart.')
        sys.exit(-1)













    #window.updateUI.start()


    #app.connect(core, QtCore.SIGNAL("new_plotdata_cam"), window.update_plot_cam)
    #app.connect(core, QtCore.SIGNAL("tick_cam"), window.refresh_cam)
    #app.connect(core, QtCore.SIGNAL("running"), window.update_running)


    #app.connect(window, QtCore.SIGNAL("start"), core.start)
    #app.connect(window, QtCore.SIGNAL("stop"), core.stop)

    


    #window.updateUI.newResultSignal.connect(core.new_result)



    window.startSignal.connect(window.start_timer)
    window.stopSignal.connect(window.stop_timer)

    window.frameGrabber1.newConfigSignal.connect(window.read_camera_config)
    window.frameGrabber2.newConfigSignal.connect(window.read_camera_config)


    # if Cam1 and cam2

    if window.cam3:
        window.frameGrabber3.newFrameSignal.connect(window.show_frame_webcam)
        # either of cam1 or cam2 is present, but not both
        if window.cam1:
            window.frameReader1.newFrameSignal.connect(window.show_frame1)

        if window.cam2:
            window.frameReader2.newFrameSignal.connect(window.show_frame1)
    else: # webcam is not present
        if window.cam1 and not window.cam2:
            # only cam1
            window.frameReader1.newFrameSignal.connect(window.show_frame1)
            window.ui.webcam_box2.setVisible(False)
        if window.cam2 and not window.cam1:
            # only cam2
            window.frameReader2.newFrameSignal.connect(window.show_frame1)
            window.ui.webcam_box2.setVisible(False)
        if window.cam1 and window.cam2:
            # both cam1 and cam2 present
            window.frameReader1.newFrameSignal.connect(window.show_frame1)
            window.frameReader2.newFrameSignal.connect(window.show_frame2)


    '''
    # First camera goes left, webcam goes right
    window.frameReader1.newFrameSignal.connect(window.show_frame1)
    window.frameGrabber3.newFrameSignal.connect(window.show_frame_webcam)

    # When we have webcam .... then
    if(window.cam3 and ~window.cam1):
        window.frameReader2.newFrameSignal.connect(window.show_frame1)
    else:
        window.frameReader2.newFrameSignal.connect(window.show_frame2)
    '''


    #app.connect(core, QtCore.SIGNAL("quit"), app.quit)

    sys.exit(app.exec_())