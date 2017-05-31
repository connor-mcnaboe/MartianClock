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
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QLCDNumber, QWidget, qApp, QAction, \
 QHBoxLayout, QVBoxLayout, QFrame, QSplitter, QStyleFactory, QLabel, QGridLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
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
		msd = str(msd).split('.')
		msdPre = msd[0]
		msdPost = msd[1]
		msdPost = msdPost[0:5]
		if 4 <= len(msd[1]) < 5:
			msdPost =  msdPost[0:3] + '0'
		elif 3<= len(msd[1]) < 5:
			msdPost = msdPost[0:2] + '00'
		elif 2 <= len(msd[1]) < 5:
			msdPost = msdPost[0:1] + '000'
		elif 1 <= len(msd[1]) < 5:
			msdPost = msdPost[0] + '0000'
		elif len(msd[1]) < 5:
			msdPost = '00000'

		msd = [msdPre, msdPost]
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
	
	def marsDistance(ma):
		helioDistance = 1.5236*(1.00436 - 0.09309*math.cos(math.radians(ma)) \
						- 0.00436*math.cos(math.radians(2*ma)) - 0.00031*math.cos(math.radians(3*ma)))
		return helioDistance

#----------------------------------#
# Distance of Mars from barycenter #
#----------------------------------#

class HelioDistance(QWidget): 
	
	def __init__(self): 
		super().__init__()
		self.initUI()
	
	def initUI(self): 
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.distance)
		self.timer.start(10)
		
		self.lcd = QLCDNumber(self)
		self.lcd.resize(400, 100)
		self.lcd.setDigitCount(8)
		self.lcd.display("Time") 
		self.lcd.setStyleSheet("background-image: url(./images/sunMars.jpg)")
		
		
	
	def distance(self): 
			 
		self.millis = MartianTime.currentTimeMillis()
		self.jdUT = MartianTime.julianDateUT(self.millis)
		self.jdTT = MartianTime.julianDateTT(self.jdUT)
		self.deltaj = MartianTime.deltatJ2000(self.jdTT)
		self.ma = MartianTime.marsMeanAnomaly(self.deltaj)
		self.au = MartianTime.marsDistance(self.ma)
		self.lcd.display(self.au) 

#------------------------------#		
# Local Mean Solar time widget #
#------------------------------#

class LocalSolarTime(QWidget): 
	
	def __init__(self):
		super().__init__()
		self.initUI()
		
	def initUI(self): 
		
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.localClock)
		self.timer.start(10)
		
		self.lcd = QLCDNumber(self)
		self.lcd.resize(400, 100)
		self.lcd.setDigitCount(8)
		self.lcd.display("Hours" + ":" + "Min" + ":" + "Sec") 
		self.lcd.setStyleSheet("background-image: url(./images/curiositySelfie.jpg)")

		
	def localClock(self): 
		 
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
		self.lmst = MartianTime.localMeanSolarTime(self.mct, 222.6)
		self.lmstClock = MartianTime.clockTime(self.lmst)
		self.lcd.display(self.lmstClock[0] + ":" + self.lmstClock[1] + ":" + self.lmstClock[2])
		
#-------------------------#
# Martian Sol date widget #
#-------------------------#

class SolDate(QWidget):

	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.sol)
		self.timer.start(10)

		self.lcd = QLCDNumber(self)
		self.lcd.resize(400, 100)
		self.lcd.setDigitCount(11)
		self.lcd.display('sol')
		self.lcd.setStyleSheet("background-image: url(./images/arabiaterra.jpg)")


	def sol(self):
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
		self.lcd.display(self.msd[0] + '.' + self.msd[1])


#-----------------------------------------#
# LCD Martian prime meridian clock widget #
#-----------------------------------------#

class LcdMct(QWidget):

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
		self.lcd.resize(400, 100)
		self.lcd.setDigitCount(8)
		self.lcd.display("Hours" + ":" + "Min" + ":" + "Sec")


		#---Style lcd numbers and display---#

		self.lcd.setStyleSheet("background-image: url(./images/arabiaterra.jpg)")


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
		self.lcd.display(self.marsClock[0] + ':' + self.marsClock[1] + ':' + self.marsClock[2])

#--------------------#
# Custom Grid widget #
#--------------------#

class LayoutWidget(QWidget):

	def __init__(self):

		super().__init__()
		self.initUI()

	def initUI(self):

		#------------------------------------#
		# Layout and initilzation of widgets #
		#------------------------------------#


		font = QFont('SansSerif', 14)
		font.setBold(True)

		#---Set Labels---#

		lblMct = QLabel(self)
		lblMct.setText('Mars \nCoordinated \nTime')
		lblMct.setFont(font)


		lblMsd = QLabel(self)
		lblMsd.setText('Mars \nSol \nDate')
		lblMsd.setFont(font)
		
		lblC = QLabel(self)
		lblC.setText(' Local \n Mean \n Solar Time') 
		lblC.setFont(font)
		
		lblHelio = QLabel(self)
		lblHelio.setText("Distance from \nbarycenter (AU)")
		lblHelio.setFont(font)


		marsClock = LcdMct()
		msd = SolDate()
		lmst = LocalSolarTime()
		helioDist = HelioDistance()
		
		
		grid = QGridLayout()
		grid.setSpacing(10)

		grid.addWidget(lblMct, 1, 0)
		grid.addWidget(marsClock, 1, 1, 5, 5)

		grid.addWidget(lblMsd, 10, 0)
		grid.addWidget(msd, 10, 1, 5, 5)
		
		grid.addWidget(lblC, 15, 0)
		grid.addWidget(lmst, 15, 1, 5, 5)
		
		grid.addWidget(lblHelio, 20, 0)
		grid.addWidget(helioDist, 20, 1, 5, 5)
		
		self.setLayout(grid)


class Main(QMainWindow, MartianTime, QWidget):

	def __init__(self):

		super().__init__()
		self.initUI()


	def initUI(self):

		#---------------#
		# Add widget(s) #
		#---------------#

		layout  = LayoutWidget()
		self.setCentralWidget(layout)

		#---------------#
		# Menubar stuff #
		#---------------#

		exitAction = QAction(QIcon('./images/exit.png'), '&Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit application')
		exitAction.triggered.connect(qApp.quit)

		self.statusBar()

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAction)

		#-------------------#
		# Main window stuff	#
		#-------------------#

		self.setGeometry(300, 300, 550, 520)
		self.setWindowTitle('Martian Clock')
		self.setWindowIcon(QIcon('./images/mars.png'))
		self.setStyleSheet("background-image: url(./images/appBackground.jpg)")
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = Main()
	sys.exit(app.exec_())
