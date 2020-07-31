
import cv2 
import os 
import sys 
import subprocess 
import re 

def get_trailing_number(s):
        m = re.search(r'\d+$', s)
        return int(m.group()) if m else None


class cameraControl(object): 
	def __init__(self, cameraID, cameraMake='C920', debug=True):
		self.cameraID = cameraID 
		self.cameraMake = cameraMake 

		self.setCommandBase = 'v4l2-ctl '+'-d'+str(self.cameraID)+' --set-ctrl'
		self.getCommandBase = 'v4l2-ctl '+'-d'+str(self.cameraID)+' --get-ctrl'
		self.debug = debug 
		if cameraMake=='C920': 
			self.minZoom = 100
			self.maxZoom = 500
			self.minExposure = 3 
			self.maxExposure = 334 # Though max is 2048, that changes frame rate this I think is 33.3 msec
			self.minGain = 0
			self.maxGain = 255 
			self.gainStep = 20
			self.exposureStep = 10

	def setAutoExpoure(self):
		if sys.platform.startswith('lin'):
			subprocess.call(self.setCommandBase +' exposure_auto=3',shell=True)



	def setManualExposure(self): 
		if sys.platform.startswith('lin'):
			subprocess.call(self.setCommandBase +' exposure_auto=1',shell=True)
		# Set exposure to 33.3 msec


	def setExposure(self,exposure):
		if sys.platform.startswith('lin'):
			if exposure <=self.maxExposure and exposure >= self.minExposure:
				subprocess.call(self.setCommandBase + ' exposure_absolute='+str(exposure),shell=True)
			else: 
				raise ValueError 


	def setGain(self,gain):
		if sys.platform.startswith('lin'):
			if gain <=self.maxGain and gain >= self.minGain:
				subprocess.call(self.setCommandBase + ' gain='+str(gain),shell=True)
			else:
				raise ValueError



	def setZoom(self,zoom): 
		if sys.platform.startswith('lin'):
			if zoom <=self.maxZoom and zoom >= self.minZoom:
				subprocess.call(self.setCommandBase + ' zoom_absolute='+str(zoom), shall=True)
			else: 
				raise ValueError


	def getExposure(self):
		if sys.platform.startswith('lin'):
			p = subprocess.Popen(self.getCommandBase + ' exposure_absolute', stdout=subprocess.PIPE, shell=True)
			output, err = p.communicate()
			exposure = get_trailing_number(output)
			return exposure 

	def getGain(self): 
		if sys.platform.startswith('lin'):
			p = subprocess.Popen(self.getCommandBase + ' gain', stdout=subprocess.PIPE, shell=True)
			output, err = p.communicate()
			gain = get_trailing_number(output)
			return gain 

	def getZoom(self):
		if sys.platform.startswith('lin'):
			p = subprocess.Popen(self.getCommandBase + ' zoom_absolute' , stdout=subprocess.PIPE, shell=True)
			output, err = p.communicate()
			zoom = get_trailing_number(output)
			return zoom 

	def increaseZoom(self):
		#if sys.platform.startswith('lin'):
		#	zoom = self.getZoom()
		pass 


	def decreaseZoom(self): 
		pass
		


	def increaseGain(self): 
		currentGain = self.getGain()
		if currentGain < self.maxGain-self.gainStep:
			newGain = currentGain+self.gainStep 
			self.setGain(newGain)
			newGainSet = self.getGain()
			return (currentGain,newGainSet)
		else:
			return None



	def decreaseGain(self):
		currentGain = self.getGain()
		if currentGain > self.minGain+self.gainStep:
			newGain = currentGain - self.gainStep
			self.setGain(newGain)
			return (currentGain,newGain)
		else:
			return None


	def increaseExposure(self): 
		currentExp = self.getExposure()
		#print currentExp
		#print self.maxExposure - self.exposureStep

		if currentExp < self.maxExposure-self.exposureStep:
			newExp = currentExp + self.exposureStep
			self.setExposure(newExp)
			return (currentExp,newExp)
		else:
			return None

	def decreaseExposure(self):
		currentExp = self.getExposure()
		#print currentExp
		#print self.minExposure + self.exposureStep
		if currentExp > self.minExposure+self.exposureStep:
			newExp = currentExp - self.exposureStep
			self.setExposure(newExp)
			return (currentExp, newExp)
		else:
			return None







