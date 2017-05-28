#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  marsClock.py
#  
#  Copyright 2017 Connor McNaboe <mcnaboeconnor@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  Algorithms from https://www.giss.nasa.gov/tools/mars24/help/algorithm.html


import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QLCDNumber, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPalette
import time 
import math 
import datetime


class MartianTime(object): 
	
		
	#---------------------------------#
	# Configure Earth Time Functions  #
	#---------------------------------#
	def currentTimeMillis(): # Convert time to milliseconds 
		currentTimeMillis = int(round(time.time()* 1000))
		return currentTimeMillis 

	def julianDateUT(millis): # Convert julian date universial time  
		julianDateUT = 2440587.5 + (millis / (8.64 * 10**7)) 
		return julianDateUT
	
	def julianDateTT(julianDateUT): # Convert to julian date Terrestrial time 
		julianDateTT = julianDateUT + ((32.184 + 37)/ (86400)) 
		return julianDateTT
		
	def deltatJ2000(julianDateTT): # Calculate time offset from J2000 Epoch
		deltatJ2000 = julianDateTT - 2451545.0
		return deltatJ2000

#----------------------------------#
#Configure Martian Time paramaters #
#----------------------------------#
	
	def marsMeanAnomaly(deltatJ2000): # Calculate the mean anomaly of the martian orbit
		maUncorrected = 19.3871 + 0.52402073*(deltatJ2000)
		n360s = int( maUncorrected / 360) * 360 
		marsMeanAnomaly = maUncorrected - n360s
		return marsMeanAnomaly

	def angleFictionMeanSun(deltatJ2000): # Calulate angle of diction mean sun 
		afmsUncorrected = 270.3871 + 0.524038496*(deltatJ2000)
		n360s = int(afmsUncorrected / 360) * 360 
		angleFictionMeanSun = afmsUncorrected - n360s
		return angleFictionMeanSun
	
	def perturbers(deltatJ2000): # Calculate perturbers
		pbs = 0.0071*math.cos(math.radians(((0.985626*deltatJ2000)/2.2353) + 49.409)) + \
			0.0057*math.cos(math.radians(((0.985626*deltatJ2000)/2.7543) + 168.173)) + \
			0.0039*math.cos(math.radians(((0.985626*deltatJ2000)/1.1177) + 191.837)) + \
			0.0037*math.cos(math.radians(((0.985626*deltatJ2000)/15.7866) + 21.736)) + \
			0.0021*math.cos(math.radians(((0.985626*deltatJ2000)/2.1354) + 15.704)) + \
			0.0020*math.cos(math.radians(((0.985626*deltatJ2000)/2.4694) + 95.528)) + \
			0.0018*math.cos(math.radians(((0.985626*deltatJ2000)/32.8493) + 49.095)) 
		return pbs

	def v_M(deltatJ2000, pbs, marsMeanAnomaly): # Determine the equation of center 
		leadingConstant = (10.691 + (3*10**(-7))*deltatJ2000) - int((10.691 + (3*10**(-7))*deltatJ2000)/360)*360
		v_M = (leadingConstant)*math.sin(math.radians(marsMeanAnomaly)) + \
			0.623*math.sin(math.radians(2*marsMeanAnomaly)) + 0.050*math.sin(math.radians(3*marsMeanAnomaly)) + \
			0.005*math.sin(math.radians(4*marsMeanAnomaly)) + 0.0005*math.sin(math.radians(5*marsMeanAnomaly))+ \
			pbs
		return v_M 

	def aerocentSolarLong(angleFictionMeanSun, v_M):
		l_s = (angleFictionMeanSun + v_M) - int((angleFictionMeanSun + v_M)/360)*360 
		return l_s 

#------------------------#
# Determine Martian Time #
#------------------------#

	def martianEquationOfTime(l_s, v_M):
		eot = 2.861*math.sin(math.radians(2*l_s)) - 0.071*math.sin(math.radians(4*l_s)) + \
			0.002*math.sin(math.radians(6*l_s)) - v_M 
		return eot
	 
	def marsSolDate(deltatJ2000):
		msd = ((deltatJ2000 - 4.5)/1.027491252) + 44796 - 0.00096
		return msd
	
	def marsCoordinatedTime(julianDateTT): 
		mct = (24* (((julianDateTT - 2451549.5)/1.0274912517) + 44769.0 - 0.0009626)) % 24
	
		return mct 

	def localMeanSolarTime(mct, deg): # Solar time for any longtitude west of the prime meridian 
		lmst = mct - deg*(1/15)
		return lmst

	def clockTime(mct):
		mctStr = str(mct)
		strHours = mctStr.split('.')
		mctHours  = strHours[0]
		strMin = str(60*float('.' + strHours[1])).split('.')
		mctMin = strMin[0]
		strSec = str(60*float('.' + strMin[1])).split('.')
		mctSec = strSec[0]
		if 1 <= len(mctSec) < 2: 
			mctSec = "0" + mctSec
		elif len(mctSec) < 1: 
			mctSec = "00"
		if 1 <= len(mctMin) < 2: 
			mctMin = "0" + mctMin
		elif len(mctMin) < 1: 
			mctMin = "00"
		if 1 <= len(mctHours) < 2: 
			mctHours = "0" + mctHours
		elif len(mctHours) < 1: 
			mctHours = "00" 
		
		mctClockTime = [mctHours , mctMin ,  mctSec]
		return mctClockTime
	
	 

#-------------------------------#
# Configure UI and display time #
#-------------------------------#

class Main(QMainWindow, MartianTime, QWidget): 
	
	def __init__(self): 
		
		super().__init__()
		

		self.initUI()
		
		
	def initUI(self): 
		
		#--------------------------------# 
		# LCD Martian Central Time clock #
		#--------------------------------#
		
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.Time)
		self.timer.start(10)
		
		self.lcd = QLCDNumber(self)
		self.lcd.resize(325, 130)
		self.lcd.setDigitCount(8)
		self.lcd.display("Hours" + ":" + "Min" + ":" + "Sec")	
		self.lcd.setStyleSheet("background-color: black")
		self.setCentralWidget(self.lcd)
		
		#-------------------#
		# Main window stuff	#
		#-------------------#
		
		self.setGeometry(300, 300, 300, 220)
		self.setWindowTitle('Martian Clock') 
		self.setWindowIcon(QIcon('mars.png'))
		
		#---Background Image---#
		self.setStyleSheet("background-image: url(./mars.jpg)")
		self.show()
		
	def Time(self): 
		
		self.millis = MartianTime.currentTimeMillis() 
		self.jdUT = MartianTime.julianDateUT(self.millis)
		self.jdTT = MartianTime.julianDateTT(self.jdUT)
		self.deltaj = MartianTime.deltatJ2000(self.jdTT)
		self.ma = MartianTime.marsMeanAnomaly(self.deltaj)
		self.fa = MartianTime.angleFictionMeanSun(self.deltaj)
		self.pert = MartianTime.perturbers(self.deltaj)
		self.vM = MartianTime.v_M(self.deltaj, self.pert, self.ma)
		self.l_s = MartianTime.aerocentSolarLong(self.fa, self.vM)
		self.eot = MartianTime.martianEquationOfTime(self.l_s, self.vM)
		self.msd = MartianTime.marsSolDate(self.deltaj)
		self.mct = MartianTime.marsCoordinatedTime(self.jdTT)
		self.marsClock = MartianTime.clockTime(self.mct)
		self.lcd.display(self.marsClock[0] + ':' + self.marsClock[1] +  ':' + self.marsClock[2]  )
	

if __name__ == '__main__':	
	app = QApplication(sys.argv)
	main = Main()
	sys.exit(app.exec_())
