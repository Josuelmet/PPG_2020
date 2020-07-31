# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'record_ui.ui'
#
# Created: Wed Nov 26 11:39:00 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import (QWidget, QLabel,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QPushButton, QGroupBox,
                             QPlainTextEdit,
                             QApplication, QLineEdit, QLCDNumber)
from pyDistancePPG.pulse_ox import DisplayForm, ConfigForm, Toolbar

import CONFIG

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


class PtGreyCameraControl(QWidget):
    def __init__(self, cameraID):
        super(PtGreyCameraControl, self).__init__()

        self.cameraID = cameraID
        self.initUI()

    def initUI(self):
        BigFont = QFont("Helvetica [Cronyx]", 12, QFont.Bold)
        self.CameraControlGrid = QGridLayout()
        self.CameraControlGrid.setSpacing(10)

        self.exposure_title = QLabel('Exposure (ms)')
        self.exposure_title.setFont(BigFont)
        self.gain_title = QLabel('Gain (dB)')
        self.gain_title.setFont(BigFont)
        self.FPS_title = QLabel('Frame rate (Fps)')
        self.FPS_title.setFont(BigFont)
        self.Binning_title = QLabel("Binning (0/1)")
        self.Binning_title.setFont(BigFont)

        self.offsetX_title = QLabel('X Offset')
        self.offsetY_title = QLabel('Y Offset')
        self.width_title = QLabel('Width')
        self.height_title = QLabel('Height')

        self.exposure_value = QLineEdit()
        self.exposure_value.setValidator(QDoubleValidator(0.00, 33.33, 2))
        self.exposure_value.setFont(BigFont)
        # self.exposure_value.setFixedWidth(5)
        self.gain_value = QLineEdit()
        self.gain_value.setValidator(QDoubleValidator(0.00, 18.00, 2))
        self.gain_value.setFont(BigFont)
        # self.gain_value.setFixedWidth(5)
        self.FPS_value = QLineEdit()
        self.FPS_value.setText('30')
        self.FPS_value.setEnabled(False)
        self.FPS_value.setFont(BigFont)

        self.Binning_value = QLineEdit()
        self.Binning_value.setFont(BigFont)

        self.offsetX_value = QLineEdit()
        self.offsetY_value = QLineEdit()
        self.width_value = QLineEdit()
        self.height_value = QLineEdit()

        self.push_cameraSetup = QPushButton()
        self.push_cameraSetup.setObjectName(str(self.cameraID))
        self.push_cameraSetup.setFont(BigFont)


        self.CameraControlGrid.addWidget(self.exposure_title, 0, 0, 1, 2)
        self.CameraControlGrid.addWidget(self.exposure_value, 0, 2, 1, 2)
        self.CameraControlGrid.addWidget(self.gain_title, 1, 0, 1, 2)
        self.CameraControlGrid.addWidget(self.gain_value, 1, 2, 1, 2)
        self.CameraControlGrid.addWidget(self.FPS_title, 2, 0, 1, 2)
        self.CameraControlGrid.addWidget(self.FPS_value, 2, 2, 1, 2)
        self.CameraControlGrid.addWidget(self.Binning_title,3, 0, 1, 2)
        self.CameraControlGrid.addWidget(self.Binning_value,3, 2, 1, 2)
        self.CameraControlGrid.addWidget(self.offsetX_title,4, 0, 1, 1)
        self.CameraControlGrid.addWidget(self.offsetX_value,4, 1, 1, 1)
        self.CameraControlGrid.addWidget(self.offsetY_title,4, 2, 1, 1)
        self.CameraControlGrid.addWidget(self.offsetY_value,4, 3, 1, 1)
        self.CameraControlGrid.addWidget(self.width_title, 5,0, 1, 1)
        self.CameraControlGrid.addWidget(self.width_value, 5,1, 1, 1)
        self.CameraControlGrid.addWidget(self.height_title,5,2, 1, 1)
        self.CameraControlGrid.addWidget(self.height_value,5,3, 1, 1)

        self.CameraControlGrid.addWidget(self.push_cameraSetup, 6, 1,1,2)
        self.setLayout(self.CameraControlGrid)


class OTEventBlock(QGroupBox):
    def __init__(self):
        super(OTEventBlock, self).__init__()

        self.initUI()

    def initUI(self):
        self.setTitle(_fromUtf8("Operating room controls"))
        self.setObjectName('OTEventBox')

        BigFont = QFont("Helvetica [Cronyx]", 12, QFont.Bold)
        self.OTBoxGrid = QGridLayout()
        self.OTBoxGrid.setSpacing(10)

        self.Event_1_title = QLabel('Anesthesia is administered')
        self.Event_1_title.setFont(BigFont)
        self.Event_2_title = QLabel('Anesthesia sets in')
        self.Event_2_title.setFont(BigFont)
        self.Event_3_title = QLabel('Emergence from Anethesia')

        self.Event_3_title.setFont(BigFont)

        self.push_Event_1 = QPushButton()
        self.push_Event_1.setObjectName(_fromUtf8("Anesthesia_start"))
        self.push_Event_1.setFont(BigFont)

        self.push_Event_2 = QPushButton()
        self.push_Event_2.setObjectName(_fromUtf8("Anesthesia_set"))
        self.push_Event_2.setFont(BigFont)

        self.push_Event_3 = QPushButton()
        self.push_Event_3.setObjectName(_fromUtf8("Anesthesia_end"))

        self.push_Event_3.setFont(BigFont)

        self.push_Event_1.setText(_translate("MainWindow", "Click Me", None))
        self.push_Event_2.setText(_translate("MainWindow", "Click Me", None))

        self.push_Event_3.setText(_translate("MainWindow", "Click Me", None))

        self.OTBoxGrid.addWidget(self.Event_1_title, 1, 0)
        self.OTBoxGrid.addWidget(self.push_Event_1, 1, 1)

        self.OTBoxGrid.addWidget(self.Event_2_title, 2, 0)
        self.OTBoxGrid.addWidget(self.push_Event_2, 2, 1)

        self.OTBoxGrid.addWidget(self.Event_3_title, 3, 0)

        self.OTBoxGrid.addWidget(self.push_Event_3, 3, 1)

        self.setLayout(self.OTBoxGrid)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1400, 900)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.centralwidget.resize(1400,900)

        ''' Structure of this GUI
        centralWidget (1400 x 900)
            verticalLayout
                horizontalLayoutTop
                    webcam_box1 (700 x 500)
                    webcam_box2 (700 x 500)
                horizontalLayoutBottom
                    controlBox  (300 x 300)
                    timer_LCD   (200 x 100) (could be (200 x 300)
                    pulseOxBox  (450 x 300)

        '''
        BigFont = QFont("Helvetica [Cronyx]", 12, QFont.Bold)
        # vertical layout allows to add widget vertically
        self.verticalLayout = QVBoxLayout()

        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        
        self.horizontalLayoutTop = QHBoxLayout()
        self.horizontalLayoutTop.setObjectName(_fromUtf8("horizontalLayoutTop"))


        self.webcam_box1 = QGroupBox(self.centralwidget)
        self.webcam_box1.setTitle(_fromUtf8("Camera Feed 1"))
        self.webcam_box1.setObjectName(_fromUtf8("webcam_box_1"))
        #self.webcam_box1.setGeometry(QtCore.QRect(0, 0, 700, 500))







        #self.webcam_box2.setGeometry(QtCore.QRect(700, 0, 700, 500))

        self.webcam1 = QLabel(self.webcam_box1)
        self.webcam1.setGeometry(QtCore.QRect(30, 30, 641, 481)) # Default image size
        self.webcam1.setText(_fromUtf8("Camera Feed 1"))
        self.webcam1.setObjectName(_fromUtf8("webcam_1"))

        self.webcam1_hBox = QHBoxLayout()

        # Camera Control
        #self.cameraControlWidget = QWidget(self.centralwidget)
        self.cameraControlWidget =[]
        self.cameraControlWidget.append(PtGreyCameraControl(0))
        self.cameraControlWidget.append(PtGreyCameraControl(1))




        #self.CameraControlGrid = QGridLayout()
        # self.CameraControlForm =QFormLayout()


        # self.FPS_value.setFixedWidth(5)




        # self.CameraControlForm.addRow(self.exposure_title, self.exposure_value)
        # self.CameraControlForm.addRow(self.gain_title,self.gain_value)
        # self.CameraControlForm.addRow(self.FPS_title,self.FPS_value)

        #self.cameraControlWidget.setLayout(self.CameraControlGrid)
        self.webcam1_hBox.addWidget(self.webcam1,3)
        self.webcam1_hBox.addWidget(self.cameraControlWidget[0],1)

        self.webcam_box1.setLayout(self.webcam1_hBox)



        # Webcam -2 // May be webcam or the second point grey

        self.webcam_box2 = QGroupBox(self.centralwidget)
        self.webcam_box2.setTitle(_fromUtf8("Camera Feed 2"))
        self.webcam_box2.setObjectName(_fromUtf8("webcam_box_2"))






        self.webcam2 = QLabel(self.webcam_box2)
        self.webcam2.setGeometry(QtCore.QRect(30, 30, 641, 481)) # Default image size
        self.webcam2.setText(_fromUtf8("Camera Feed 2"))
        self.webcam2.setObjectName(_fromUtf8("webcam_2"))










        self.webcam2_vBox = QHBoxLayout()
        self.webcamControlWidget = QWidget(self.centralwidget)

        self.webcam2_hBoxBottom = QVBoxLayout()

        self.push_inc_webcam_gain = QPushButton()
        self.push_inc_webcam_gain.setObjectName(_fromUtf8("increase_webcam_gain"))
        self.push_inc_webcam_gain.setFont(BigFont)

        self.push_dec_webcam_gain = QPushButton()
        self.push_dec_webcam_gain.setObjectName(_fromUtf8("decrease_webcam_gain"))
        self.push_dec_webcam_gain.setFont(BigFont)

        self.push_inc_webcam_exp = QPushButton()
        self.push_inc_webcam_exp.setObjectName(_fromUtf8("increase_webcam_exposure"))
        self.push_inc_webcam_exp.setFont(BigFont)

        self.push_dec_webcam_exp = QPushButton()
        self.push_dec_webcam_exp.setObjectName(_fromUtf8("decrease_webcam_exposure"))
        self.push_dec_webcam_exp.setFont(BigFont)

        self.webcam2_hBoxBottom.addWidget(self.push_inc_webcam_exp)
        self.webcam2_hBoxBottom.addWidget(self.push_dec_webcam_exp)
        self.webcam2_hBoxBottom.addWidget(self.push_inc_webcam_gain)
        self.webcam2_hBoxBottom.addWidget(self.push_dec_webcam_gain)

        self.webcamControlWidget.setLayout(self.webcam2_hBoxBottom)

        self.webcam2_vBox.addWidget(self.webcam2,3)
        #FIXME: Need to implement both webcam and point grey here
        self.webcam2_vBox.addWidget(self.cameraControlWidget[1],1)


        self.webcam_box2.setLayout(self.webcam2_vBox)
        self.OTEventBlock = OTEventBlock()

        if CONFIG.PROFILE==0: #Operating room profile

            self.horizontalLayoutTop.addWidget(self.webcam_box1, 2)
            self.cameraControlWidget[0].Binning_value.setEnabled(False)
            self.cameraControlWidget[0].offsetX_value.setEnabled(False)
            self.cameraControlWidget[0].offsetY_value.setEnabled(False)
            self.cameraControlWidget[0].width_value.setEnabled(False)
            self.cameraControlWidget[0].height_value.setEnabled(False)

            self.horizontalLayoutTop.addWidget(self.OTEventBlock,1)
        else:
            self.horizontalLayoutTop.addWidget(self.webcam_box1, 1)
            self.horizontalLayoutTop.addWidget(self.webcam_box2,1)

        #self.horizontalLayoutTop.addWidget(self.perfusion_box)

        self.horizontalLayoutBottom = QHBoxLayout()
        self.horizontalLayoutBottom.setObjectName(_fromUtf8("horizontalLayoutBottom"))


        # Application controls

        self.control_box = QGroupBox(self.centralwidget)
        self.control_box.setTitle(_fromUtf8("Controls"))
        self.control_box.setObjectName(_fromUtf8("control_box"))
        self.control_box.setGeometry(QtCore.QRect(0,0, 300, 300))


        self.control_vBox = QVBoxLayout()
        self.control_hBoxTop = QHBoxLayout()

        self.push_setup = QPushButton()
        # self.push_setup.setGeometry(QtCore.QRect(80, 20, 81, 23))
        self.push_setup.setObjectName(_fromUtf8("push_setup"))
        self.push_setup.setFont(BigFont)

        self.push_start = QPushButton()
        # self.push_start.setGeometry(QtCore.QRect(190, 20, 81, 23))
        self.push_start.setObjectName(_fromUtf8("push_start"))
        self.push_start.setFont(BigFont)

        self.push_stop = QPushButton()
        # self.push_stop.setGeometry(QtCore.QRect(300, 20, 81, 23))
        self.push_stop.setObjectName(_fromUtf8("push_stop"))
        self.push_stop.setFont(BigFont)

        self.push_process = QPushButton()
        # self.push_process.setGeometry(QtCore.QRect(80, 50, 81, 23))
        self.push_process.setObjectName(_fromUtf8("push_process"))
        self.push_process.setFont(BigFont)

        self.control_hBoxTop.addWidget(self.push_start)
        self.control_hBoxTop.addWidget(self.push_stop)
        self.control_hBoxTop.addWidget(self.push_setup)

        self.plain_instruction = QPlainTextEdit(self.control_box)
        self.plain_instruction.setGeometry(QtCore.QRect(0, 100, 400, 300))
        self.plain_instruction.setObjectName(_fromUtf8("plain_instruction"))
        self.plain_instruction.setCenterOnScroll(True)
        self.plain_instruction.setReadOnly(True)

        self.control_vBox.addLayout(self.control_hBoxTop)
        self.control_vBox.addWidget(self.plain_instruction)

        self.control_box.setLayout(self.control_vBox)

        '''

        self.push_setup = QPushButton(self.control_box)
        self.push_setup.setGeometry(QtCore.QRect(80, 20, 81, 23))
        self.push_setup.setObjectName(_fromUtf8("push_setup"))
        
        self.push_start = QPushButton(self.control_box)
        self.push_start.setGeometry(QtCore.QRect(190, 20, 81, 23))
        self.push_start.setObjectName(_fromUtf8("push_start"))

        self.push_stop = QPushButton(self.control_box)
        self.push_stop.setGeometry(QtCore.QRect(300, 20, 81, 23))
        self.push_stop.setObjectName(_fromUtf8("push_stop"))

        self.push_process = QPushButton(self.control_box)
        self.push_process.setGeometry(QtCore.QRect(80, 50, 81, 23))
        self.push_process.setObjectName(_fromUtf8("push_process"))

        self.plain_instruction = QPlainTextEdit(self.control_box)
        self.plain_instruction.setGeometry(QtCore.QRect(0, 100, 400, 300))
        self.plain_instruction.setObjectName(_fromUtf8("plain_instruction"))
        self.plain_instruction.setCenterOnScroll(True)
        self.plain_instruction.setReadOnly(True)
        '''

        # Pulse Oximeter output 
        self.pulseOx_box = QGroupBox(self.centralwidget)
        self.pulseOx_box.setTitle(_fromUtf8("Pulse oximeter recordings"))
        self.pulseOx_box.setObjectName(_fromUtf8("pulseox_Output"))
        #self.pulseOx_box.setGeometry(0, 0, 450, 300)

        self.pulseOxLayout = QVBoxLayout()


        # PULSE oximeter
        self.pulseOx = DisplayForm()
        self.pulseOx2 = DisplayForm()
        #self.pulseOx.setGeometry(8,8,450,150)
        #self.pulseOx1.setGeometry(8,8,450,150)


        self.pulseOxLayout.addWidget(self.pulseOx)
        if CONFIG.PROFILE:
            self.pulseOxLayout.addWidget(self.pulseOx2)

        self.pulseOx_box.setLayout(self.pulseOxLayout)


        # Timer
        self.timer_lcd = QLCDNumber(self.centralwidget)
        self.timer_lcd.setObjectName(_fromUtf8("pulseox_Output"))
        self.timer_lcd.setGeometry(10, 10, 200, 100)


        self.horizontalLayoutBottom.addWidget(self.control_box,2)
        self.horizontalLayoutBottom.addWidget(self.timer_lcd,1)
        self.horizontalLayoutBottom.addWidget(self.pulseOx_box,2)
        

        self.verticalLayout.addLayout(self.horizontalLayoutTop,3)
        self.verticalLayout.addLayout(self.horizontalLayoutBottom,2)

        self.centralwidget.setLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)


        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        #self.config_form = ConfigForm()
        #self.toolbar = Toolbar()

        # Group controls 
        '''
        self.label_2 = QLabel(self.control_box)
        self.label_2.setGeometry(QtCore.QRect(30, 20, 71, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.push_check = QPushButton(self.control_box)
        self.push_check.setGeometry(QtCore.QRect(80, 40, 81, 23))
        self.push_check.setObjectName(_fromUtf8("push_check"))
        self.push_close = QPushButton(self.control_box)
        self.push_close.setGeometry(QtCore.QRect(190, 40, 81, 23))
        self.push_close.setObjectName(_fromUtf8("push_close"))
        
        self.push_browse = QPushButton(self.control_box)
        self.push_browse.setGeometry(QtCore.QRect(80, 120,81,23))
        self.push_browse.setObjectName(_fromUtf8('push_browse'))
        self.label = QLabel(self.control_box)
        self.label.setGeometry(QtCore.QRect(30, 150, 91, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.plain_instruction = QPlainTextEdit(self.control_box)
        self.plain_instruction.setGeometry(QtCore.QRect(30, 180, 300, 300))
        self.plain_instruction.setObjectName(_fromUtf8("plain_instruction"))
        self.plain_instruction.setCenterOnScroll(True)
        self.plain_instruction.setReadOnly(True)
        #self.plain_instruction.setMaximumBlockCount(20)
        # Group_Frame
        
        
        self.horizontalLayoutBottom = QHBoxLayout()
        self.horizontalLayoutBottom.setObjectName(_fromUtf8("horizontalLayoutBottom"))
        
        # Group_Output 
        self.Group_Output = QGroupBox(self.centralwidget)
        self.Group_Output.setTitle(_fromUtf8("distancePPG Output"))
        self.Group_Output.setObjectName(_fromUtf8("Group_Output"))
        self.label_3 = QLabel(self.Group_Output)
        self.label_3.setGeometry(QtCore.QRect(20, 20, 130, 15))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.line_HR = QLCDNumber(self.Group_Output)
        self.line_HR.setGeometry(QtCore.QRect(20, 40, 100, 100))
        self.line_HR.setObjectName(_fromUtf8("line_HR"))
        self.label_4 = QLabel(self.Group_Output)
        self.label_4.setGeometry(QtCore.QRect(20, 140, 130, 15))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.SQDisplay = QLCDNumber(self.Group_Output)
        self.SQDisplay.setGeometry(QtCore.QRect(20, 160, 100, 100))
        self.SQDisplay.setObjectName(_fromUtf8("SQDisplay"))
        self.label_6= QLabel(self.Group_Output)
        self.label_6.setGeometry(QtCore.QRect(20, 260, 130, 15))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.motion = QLCDNumber(self.Group_Output)
        self.motion.setGeometry(QtCore.QRect(20, 280, 100, 100))
        self.motion.setObjectName(_fromUtf8("motion"))
        #self.frame_HRV = matplotlibWidget(self.Group_Output)
        #self.frame_HRV.setGeometry(QtCore.QRect(20, 90, 191, 141))
        #self.frame_HRV.setObjectName(_fromUtf8("frame_HRV"))
        #self.label_4 = QLabel(self.Group_Output)
        #self.label_4.setGeometry(QtCore.QRect(20, 70, 54, 12))
        #self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QLabel(self.Group_Output)
        self.label_5.setGeometry(QtCore.QRect(230, 10, 200, 12))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        
        self.cameraPPG = CameraForm(self.Group_Output)
        self.cameraPPG.setGeometry(QtCore.QRect(230, 22, 500, 400))
        self.cameraPPG.setObjectName(_fromUtf8("camera_PPG"))
        #self.verticalLayout_2.addWidget(self.Group_Output)
        #self.verticalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayoutTop)
        self.verticalLayout.addLayout(self.horizontalLayoutBottom)
        self.centralwidget.setLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        
        #menubar 
        
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 696, 18))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuSave = QtGui.QMenu(self.menubar)
        self.menuSave.setObjectName(_fromUtf8("menuSave"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionCurrent_Dir = QtGui.QAction(MainWindow)
        self.actionCurrent_Dir.setObjectName(_fromUtf8("actionCurrent_Dir"))
        self.actionChange_Dir = QtGui.QAction(MainWindow)
        self.actionChange_Dir.setObjectName(_fromUtf8("actionChange_Dir"))
        self.menubar.addAction(self.menuSave.menuAction())
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        '''
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "PerfusionCam Demo", None))
        self.push_start.setText(_translate("MainWindow", "Start", None))
        self.push_stop.setText(_translate("MainWindow", "Stop", None))
        self.push_setup.setText(_translate("MainWindow", "Setup", None))
        self.push_process.setText(_translate("MainWindow", "Process", None))
        self.push_inc_webcam_gain.setText(_translate("MainWindow", "Inc. Gain", None))
        self.push_dec_webcam_gain.setText(_translate("MainWindow", "Dec. Gain", None))
        self.push_inc_webcam_exp.setText(_translate("MainWindow", "Inc. Exposure", None))
        self.push_dec_webcam_exp.setText(_translate("MainWindow", "Dec. Exposure", None))
        self.cameraControlWidget[0].push_cameraSetup.setText(_translate("MainWindow", "Update Settings", None))
        self.cameraControlWidget[1].push_cameraSetup.setText(_translate("MainWindow", "Update Settings", None))

        #self.label.setText(_translate("MainWindow", "Status:", None))
        #self.label_2.setText(_translate("MainWindow", "Controls:", None))
        #self.push_check.setText(_translate("MainWindow", "Check ", None))
        #self.push_close.setText(_translate("MainWindow", "Close", None))
        #self.push_browse.setText(_translate("MainWindow", "Select Folder", None))
        #self.label_3.setText(_translate("MainWindow", "BR (Br PM)", None))
        #self.label_4.setText(_translate("MainWindow", "Signal Quality:", None))
        #self.label_5.setText(_translate("MainWindow", "Camera PPG Waveform:", None))
        #self.label_6.setText(_translate("MainWindow", "LF/HF (using PRV):", None))


        
        #self.menuSave.setTitle(_translate("MainWindow", "File", None))
#self.actionCurrent_Dir.setText(_translate("MainWindow", "Current Dir", None))
        #self.actionChange_Dir.setText(_translate("MainWindow", "Change Dir", None))