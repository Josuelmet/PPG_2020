#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  This file is part of GLExOx.
#
#  GLExOx is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  GLExOx is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with GLExOx.  If not, see <http://www.gnu.org/licenses/>.


# (C) 2011 Greg Courville <greg_courville@greglabs.com>


import sys
import serial
import array
import numpy
import os
import re
from PyQt5 import Qt, QtGui, QtCore
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtWidgets import (QWidget, QFrame, QLabel, QToolBar, QAction,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QComboBox, QPushButton, QInputDialog, QGroupBox,
                             QDialogButtonBox)
import qwt as Qwt
from datetime import datetime
import subprocess



class CMS50D(object):
    #TODO: Properly decode "finger out" flag, assuming it exists
    def __init__(self, portstr):
        self.port = serial.Serial(portstr, 115200, timeout=0.1, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, xonxoff=1)
        self.current_bpm = None
        self.current_spo2 = None
        self._buf = array.array('B')
        
    '''
    def get_data(self):
        self._buf.fromstring(self.port.read(128))
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
    def get_data(self):
        readings = {}
        
        # Instead of capturing the normal 9 bytes,
        # capture 18 bytes b/c the loop this function is called from usually
        # runs at 30Hz, which is half as fast as the pulse oximeter sends data.
        raw = self.port.read(self.buffer_length)
        if len(raw) < self.buffer_length:
            self.buffer_length = 9
            return {"spo2":0, "pulseRate":0, "pulseWaveform":0}
        
        self.buffer_length = 18
        readings["spo2"] = raw[6] & 0x7f
        readings["pulseRate"]   = raw[5] & 0x7f
        readings["pulseWaveform"] = raw[3] & 0x7f
        print(raw[5] & 0x7f)
        return readings
    
    def close(self):
        self.port.close()


# For showing data from pulse-oximeter 

class ConfigForm(QWidget):
    class PortSelector(QWidget):
        tty_pfxs = ("ttyUSB",)
        def __init__(self, *args):
            QWidget.__init__(self, *args)
            self.setLayout(QHBoxLayout())
            self.layout().setContentsMargins(0,0,0,0)
            self._combo = QComboBox()
            self._button = QPushButton("...")
            self.layout().addWidget(self._combo, 1)
            self.layout().addWidget(self._button, 0)
            self.rescan()
            self.connect(self._button, QtCore.SIGNAL("clicked()"), self.show_prompt)
        def value(self):
            return self._combo.itemText(self._combo.currentIndex())
        def set_value(self, text):
            found = False
            for i in range(self._combo.count()):
                if self._combo.itemText(i) == text:
                    self._combo.setCurrentIndex(i)
                    found = True
                    break
            if not found:
                self.set_custom(text)
        def set_custom(self, text):
            if self._custom_port:
                self._combo.removeItem(0)
            self._combo.insertItem(0, text)
            self._combo.setCurrentIndex(0)
            self._custom_port = True
        def show_prompt(self):
            text, ok = QInputDialog.getText(self, "Custom entry", "Port", text="/dev/")
            if ok:
                self.set_custom(text)
        def rescan(self):
            self._combo.clear()
            self._custom_port = False
            for x in os.listdir("/dev/"):
                for y in self.tty_pfxs:
                    if x[:len(y)] == y:
                        self._combo.addItem("/dev/" + x)
                        break
            #TODO: add Windows-compatible portscan

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setWindowTitle("GLExOx configuration")
        self.inp_hwtype = QComboBox()
        self.inp_hwtype.addItem("Contec CMS50D+")
        self.inp_hwtype.setEnabled(False)
        self.inp_port = self.PortSelector()
        comms_grp = QGroupBox("Hardware")
        comms_grp.setLayout(QGridLayout())
        comms_grp.layout().addWidget(QLabel("Device"),0,0)
        comms_grp.layout().addWidget(self.inp_hwtype,0,1)
        comms_grp.layout().addWidget(QLabel("Port"),1,0)
        comms_grp.layout().addWidget(self.inp_port,1,1)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply | QDialogButtonBox.Reset)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(comms_grp)
        #self.layout().addWidget(logging_grp)
        self.layout().addWidget(self.buttons)
        self.connect(self.buttons.button(self.buttons.Ok), QtCore.SIGNAL("clicked()"), self.close)
        self.connect(self.buttons.button(self.buttons.Ok), QtCore.SIGNAL("clicked()"), self.commit)
        self.connect(self.buttons.button(self.buttons.Apply), QtCore.SIGNAL("clicked()"), self.commit)
        self.connect(self.buttons.button(self.buttons.Cancel), QtCore.SIGNAL("clicked()"), self.reset)
        self.connect(self.buttons.button(self.buttons.Cancel), QtCore.SIGNAL("clicked()"), self.close)
        self.settings = {
            "port": str(self.inp_port.value()),
            }
        self.reset()
    def commit(self):
        self.emit(QtCore.SIGNAL("new_config"))
    def reset(self):
        if "port" in self.settings:
            self.inp_port.set_value(self.settings["port"])
    def lock_settings(self, lock):
        if lock:
            self.buttons.button(self.buttons.Ok).setEnabled(False)
            self.buttons.button(self.buttons.Apply).setEnabled(False)
        else:
            self.buttons.button(self.buttons.Ok).setEnabled(True)
            self.buttons.button(self.buttons.Apply).setEnabled(True)



class DataPlot(Qwt.QwtPlot):
    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
        self.setCanvasBackground(Qt.Qt.black)
        self.x = range(0,400)
        self.y = numpy.zeros(len(self.x))
        self.curves = (Qwt.QwtPlotCurve(),Qwt.QwtPlotCurve())
        for n in (0,1):
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(255-127*n,0,0))
            self.curves[n].setPen(pen)
            self.curves[n].attach(self)
        self.enableAxis(Qwt.QwtPlot.yLeft,False)
        self.enableAxis(Qwt.QwtPlot.xBottom,False)
        self.setAxisScale(Qwt.QwtPlot.yLeft,0,127)
        self.setAxisScale(Qwt.QwtPlot.xBottom,0,400)
        self.i = 0
    def add_data(self, newdata):
        for x in newdata:
            self.y[self.i] = x
            self.i += 1
            if self.i >= len(self.y):
                self.i = 0
        self.curves[0].setData(self.x[:self.i], self.y[:self.i])
        self.curves[1].setData(self.x[self.i+25:], self.y[self.i+25:])
    def flush_plot(self):
        self.x = range(0,400)
        self.y = numpy.zeros(len(self.x))
        self.i = 0


class Winkenlight(QWidget):
    on_color = (255,90,90)
    off_color = (80,0,0)
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.setMinimumSize(30,30)
        self._pen = Qt.QPen()
        self._pen.setWidth(5)
        self._brush = QBrush(QColor(255,255,0))
        self._ts = QtCore.QDateTime.currentDateTime().toPyDateTime()
        self._cold = (self.on_color[0]-self.off_color[0], self.on_color[1]-self.off_color[1], self.on_color[2]-self.off_color[2])
    def resizeEvent(self, foo):
        self.update()
    def paintEvent(self, foo):
        td = QtCore.QDateTime.currentDateTime().toPyDateTime() - self._ts
        lum = pow(.67,pow((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)/75000.,1.33))
        r = int(self.off_color[0] + lum*self._cold[0])
        g = int(self.off_color[1] + lum*self._cold[1])
        b = int(self.off_color[2] + lum*self._cold[2])
        self._brush.setColor(QColor(r,g,b))
        self._pen.setColor(QColor(r*2/3,g*2/3,b*2/3))
        p = QPainter(self)
        diam = min(self.width(),self.height()) * 2 / 3
        x = (self.width()-diam)/2
        y = (self.height()-diam)/2
        p.setPen(self._pen)
        p.setBrush(self._brush)
        p.drawEllipse(x,y,diam,diam)
    def ping(self):
        self._rgb = list(self.on_color)
        self._ts = QtCore.QDateTime.currentDateTime().toPyDateTime()

class NumLabel(QFrame):
    class ValueLabel(QLabel):
        def __init__(self, *args):
            QLabel.__init__(self, *args)
            self.font().setFixedPitch(True)
            self.setMinimumSize(64,64)
        def resizeEvent(self, foo):
            foo = self.font()
            foo.setPixelSize(self.height()*3/4)
            self.setFont(foo)
    def __init__(self, name_text="", *args):
        QFrame.__init__(self, *args)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.font().setFixedPitch(True)
        self.name_label = QLabel(name_text)
        self.name_label.setAlignment(Qt.Qt.AlignLeft | Qt.Qt.AlignTop)
        self.value_label = self.ValueLabel("?")
        self.value_label.setAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.name_label,1)
        self.layout.addWidget(self.value_label,8)
        self.setLayout(self.layout)
    def setText(self, *args):
        self.value_label.setText(*args)

class DisplayForm(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.plot = DataPlot()
        self.blinker = Winkenlight()
        #self.ox_label = self.NumLabel(name_text = "SpO<sub>2</sub> (%)")
        #self.ox_avg_label = self.NumLabel(name_text = "SpO<sub>2</sub> (%), 1-min. avg.")
        self.hr_label = NumLabel(name_text = "HR (bpm) [Using pulse oximeter]")
        #self.hr_avg_label = self.NumLabel(name_text = "HR (bpm), 1-min. avg.")
        self.lo_top = QHBoxLayout()
        #self.lo_top.addWidget(self.ox_label)
        #self.lo_top.addWidget(self.ox_avg_label)
        self.lo_top.addWidget(self.hr_label)
        #self.lo_top.addWidget(self.hr_avg_label)
        self.lo_bottom = QHBoxLayout()
        self.lo_bottom.addWidget(self.plot, 9)
        self.lo_bottom.addWidget(self.blinker, 1)
        self.lo_outer = QVBoxLayout()
        self.lo_outer.addLayout(self.lo_bottom, 1)
        #self.lo_outer.addLayout(self.lo_top, 1)
        self.setLayout(self.lo_outer)

class CameraForm(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        self.plot = DataPlot()
        #self.ox_label = self.NumLabel(name_text = "SpO<sub>2</sub> (%)")
        #self.ox_avg_label = self.NumLabel(name_text = "SpO<sub>2</sub> (%), 1-min. avg.")
        self.hr_label = NumLabel(name_text = "HR (bpm) [Using camera]")
        #self.hr_avg_label = self.NumLabel(name_text = "HR (bpm), 1-min. avg.")
        self.lo_top = QHBoxLayout()
        #self.lo_top.addWidget(self.ox_label)
        #self.lo_top.addWidget(self.ox_avg_label)
        self.lo_top.addWidget(self.hr_label)
        #self.lo_top.addWidget(self.hr_avg_label)
        self.lo_bottom = QHBoxLayout()
        self.lo_bottom.addWidget(self.plot)
        self.lo_outer = QVBoxLayout()
        self.lo_outer.addLayout(self.lo_bottom, 1)
        self.lo_outer.addLayout(self.lo_top, 1)
        self.setLayout(self.lo_outer)



# This toolbar can go directly to the buttons 
class Toolbar(QToolBar):
    class StartStopAction(QAction):
        def disable(self):
            self.setEnabled(False)
        def enable(self):
            self.setEnabled(True)
    def __init__(self, *args):
        QToolBar.__init__(self, *args)
        self.start = self.StartStopAction("Start", None)
        self.stop = self.StartStopAction("Stop", None)
        self.stop.setEnabled(False)
        self.config = QAction("Setup...", None)
        self.reset = QAction("Stat reset", None)
        #self.quit = QAction("Quit", None)
        self.connect(self.start, QtCore.SIGNAL("triggered()"), self.start.disable)
        self.connect(self.stop, QtCore.SIGNAL("triggered()"), self.stop.disable)
        self.addAction(self.start)
        self.addAction(self.stop)
        self.addAction(self.reset)
        self.addSeparator()
        self.addAction(self.config)
        #self.addSeparator()
        #self.addAction(self.quit)




