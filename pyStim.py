# pyStim v1.2
# _________________
# Works with microcontrollers that have hardward DACs, like the Teensy 3 line.
# It is intended to be used with a Teensy3.5/3.6, both of which have 2 analog outs.
#
# You need to load 'teensyStim.ino' onto your teensy (or cortex MC).

# Chris Deister - cdeister@brown.edu
# Anything that is licenseable is governed by an MIT License in the github directory. 

# todo: amp CSV; end session button behavior; 
# minor animal meta self.animalID_tv.set(os.path.basename(self.selectPath))


# *****************************
# **** Import Dependencies ****
# *****************************

from tkinter import *
import tkinter.filedialog as fd
import serial
import numpy as np
import matplotlib 
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import time
import datetime
import random
import struct
import sys
import os
import pandas as pd
import scipy.stats as stats
import threading

class psVariables:

	def setSessionVars(self,idString):

		# edit the default dict if you like
		a=idString in dir(self)

		# 2) If it does not exist make it
		if a==0:
			sesVarD = {'currentSession':0,'dirPath':"/",\
			'animalID':"an1",'totalTrials':5,'uiUpdateSamps':250,'sRate':1000,\
			'sampsToPlot':5000,'comPath':"/dev/cu.usbmodem3165411",'fps':15,\
			'baudRate':115200,'dacMaxVal':3.3,'dacMinVal':0,'adcBitDepth':12,\
			'dacBitDepth':12,'varCount':15,'sNum':1,'dataCount':13,\
			'tNum':1,'tDur':4,'timeToPlot':1,'cntrFreqA':0,'cntrFreqB':0}

		elif a==1:

			sesVarD=eval('self.{}'.format(idString))


		exec('self.{}=sesVarD'.format(idString))

		psUtil.refreshGuiFromDict(self,sesVarD)
		psVariables.dictToPandas(self,sesVarD,idString)

	def setPulseTrainVars(self,idString):
		
		# 1) See if the dict exists
		a=idString in dir(self)

		# 2) If it does not exist make it
		if a==0:
			ptVarD = {'dwellTime':0.005,'pulseTime':0.05,'nPulses':20,\
			'pulseAmpV':1.3,'baselineTime':0.5,'stimType':1}
		
		elif a==1:
		
			ptVarD=eval('self.{}'.format(idString))

		# 3 Then assign dir (self) variables to be the entries.
		# This is a legacy thing. 
		exec('self.{}=ptVarD'.format(idString))
		
		# 4) Update the gui if need be.
		psUtil.refreshGuiFromDict(self,ptVarD)
		
		# 4 make/update a pandas compatible frame/series for saving.
		psVariables.dictToPandas(self,ptVarD,idString)

	def dictToPandas(self,dictName,idString):
		tLab=[]
		tVal=[]
		for key in list(dictName.keys()):
			tLab.append(key)
			tVal.append(dictName[key])
		exec('self.{}_Bindings=pd.Series(tVal,index=tLab)'.format(idString))

	def pandasToDict(self,pdName,dictName,colNum):
		
		varIt=0
		csvNum=0

		for k in list(pdName.index):
			
			if len(pdName.shape)>1:
				a=pdName[colNum][varIt]
				csvNum=pdName.shape[1]
			elif len(pdName.shape)==1:
				a=pdName[varIt]

			try:
				a=float(a)
				if a.is_integer():
					a=int(a)
				dictName[k]=a
				varIt=varIt+1

			except:
				dictName[k]=a
				varIt=varIt+1
		
		return csvNum

	def loadMeta(self,dCol,path):
		
		aa=path
		bb=os.path.basename(aa)
		cc=bb.split('.')

		tempMeta=pd.read_csv(aa,index_col=0,header=None)
		gg=tempMeta.index	
		dictName='self.' + cc[0]
		exec('self.{}_pandaFrame=tempMeta'.format(cc[0]))

		for x in range(0,len(gg)):
			try:
				a=tempMeta.iloc[x][dCol]
				tKey=gg[x]

				try:
					a=float(a)
					if a.is_integer():
						a=int(a)
					exec('{}["{}"]={}'.format(dictName,tKey,a))
				except:
					try:
						exec('{}["{}"]="{}"'.format(dictName,tKey,a))						
					except:
						a

			except:
				a=1+1

class psData:

	def initSessionData(self):
		psData.sessionStores='trialNumber','trialTime','preTime','stimType',\
		'trialDuration','stimAmp_ChanA','stimAmp_ChanB'
		for x in range(0,len(psData.sessionStores)):
			exec('psData.{}=[]'.format(psData.sessionStores[x]))

	def initTrialData(self):
		psData.trialStores='tm','aOut1','aOut2','aIn1','aIn2','aIn3','aIn4','aIn5','aIn6','cnt1','cnt2','pS'
		psData.trialStoresIDs=[1,2,3,4,5,6,7,8,9,10,11,12]
		for x in range(0,len(psData.trialStores)): 
			exec('psData.{}=[]'.format(psData.trialStores[x]))

	def initTeensyStateData(self):

		psData.varHeader='','a','b','c','d','e','f','g','h','i','j','k','l','m','n'	
		psData.varNames='head','state','pDurA','iPIntA','pAmpA','nPulsesA','bDurA',\
		'pDurB','iPIntB','pAmpB','nPulsesB','bDurB','tDur','cntrFreqA','cntrFreqB'
		psData.varNums=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]

	def saveTrialData(self):

		animalID=self.sesVarD['animalID']
		tNum=int(self.sesVarD['tNum'])
		tCo=[]
		for x in range(0,len(trialStores)):
			exec('tCo={}'.format(trialStores[x]))
			if x==0:
				rf=pd.DataFrame({'{}'.format(trialStores[x]):tCo})
			elif x != 0:
				tf=pd.DataFrame({'{}'.format(trialStores[x]):tCo})
				rf=pd.concat([rf,tf],axis=1)

		rf.to_csv('{}_trial_{}.csv'.format(animalID,tNum))
		self.trialTime.append(self.teTime)
		self.preTime.append(self.tpTime)
		print('{}_trial_{} done; pre took {}'.format(animalID,tNum,tpTime))

class psPlot:
	
	def trialPlotFig(self):
		
		# initialize the data containers so we can query the labels.
		psData.initTrialData(self)

		# make a list of colors to use
		self.chanColors="olive","cornflowerblue","red","olive","cornflowerblue","red","olive","cornflowerblue","red"
		 #,"black","yellow","green","blue"
		
		# initialize containers to store line names and colors
		self.curLines=[]
		self.curColors=[]
		self.chansToPlotNow=[3,4,5]
		for x in self.chansToPlotNow:
			self.curLines.append(psData.trialStores[x])
			# if there is a color for that index use it
			try:
				self.curColors.append(self.chanColors[x])
			# otherwise use black
			except:
				self.curColors.append("black")
		

		self.lastLines="aIn1","aIn2"
		self.lastColors="olive","cornflowerblue"

		tNum=int(self.sesVarD['tNum'])-(self.lastTrial)
		totTr=int(self.sesVarD['totalTrials'])
		maxTime=int(self.sesVarD['tDur'])*int(self.sesVarD['sRate'])
		
		useDark=0
		if useDark:
			plt.style.use('dark_background')

		self.trialFramePosition='+360+0' # can be specified elsewhere
		self.updateTrialAxes=0
		self.trialPlotFig_fontSize=10
		fSz=self.trialPlotFig_fontSize
		fNum=100

		
		# Make the trial figure.
		self.trialFig = plt.figure(fNum,figsize=(5,5), dpi=100)
		self.trialFig.suptitle('trial # {} of {}'.format(tNum,totTr),fontsize=fSz)
		self.trialFig.subplots_adjust(wspace=0.1,hspace=0.2)
		
		mng = plt.get_current_fig_manager()
		eval('mng.window.wm_geometry("{}")'.format(self.trialFramePosition))

		# Top is current ongoing trial
		self.curReadAx_yLim=[-100,4196]
		self.curReadAx_xLim=[0,maxTime]

		self.curReadAx=plt.subplot2grid([2,2],(0,0),colspan=2,rowspan=1)
		# self.curReadAx.set_yticks([])
		self.curReadAx.set_xticks([])
		self.curReadAx.set_ylim([self.curReadAx_yLim[0],self.curReadAx_yLim[1]])
		self.curReadAx.set_xlim([self.curReadAx_xLim[0],self.curReadAx_xLim[1]])
		self.curReadAx.set_title('current trial',fontsize=fSz)

		# Initialize the lines that we will track. 
		for x in range(0,len(self.curLines)):
			exec('self.{},=self.curReadAx.plot([1,1],color="{}",lw=1)'.\
				format(self.curLines[x],self.curColors[x]))

		plt.show(block=False)

		# Bottom is the last trial.
		self.lastAx_yLim=[-100,4196]
		self.lastAx_xLim=[0,maxTime]

		self.lastAx=plt.subplot2grid([2,2],(1,0),colspan=2,rowspan=1)
		self.lastAx.set_ylim([self.lastAx_yLim[0],self.lastAx_yLim[1]])
		self.lastAx.set_xlim([self.lastAx_xLim[0],self.lastAx_xLim[1]])
		self.lastAx.set_title('last trial',fontsize=10)

		for x in range(0,len(self.lastLines)):
			exec('self.last_{},=self.lastAx.plot([1,1],color="{}",lw=1)'.\
				format(self.lastLines[x],self.lastColors[x]))
		
		plt.show(block=False)

	def updateTrialFig(self):

		tNum=int(self.sesVarD['tNum'])-(self.lastTrial)
		totTr=int(self.sesVarD['totalTrials'])
		maxTime=int(self.sesVarD['tDur'])*int(self.sesVarD['sRate'])

		splt=int(self.sesVarD['sampsToPlot'])
		x0=np.array(psData.tm[-int(splt):])

		for x in range(0,len(self.curLines)):
			exec('yData_{}=np.array(psData.{}[-int({}):])'.format(self.curLines[x],self.curLines[x],splt))
		
		self.curReadAx_xLim=[0,maxTime]
		self.lastAx.set_xlim([0,maxTime])
		self.curReadAx.set_xlim([0,maxTime])
		
		
		self.trialFig.suptitle('trial # {} of {}'.format(tNum,totTr),fontsize=10)
		
		if len(x0)>1:
			for x in range(0,len(self.curLines)):
				exec('self.{}.set_xdata(x0)'.format(self.curLines[x]))
				exec('self.{}.set_ydata(yData_{})'.format(self.curLines[x],self.curLines[x]))
				exec('self.curReadAx.draw_artist(self.{})'.format(self.curLines[x]))
			self.curReadAx.draw_artist(self.curReadAx.patch)
			self.trialFig.canvas.draw_idle()

		self.trialFig.canvas.flush_events()

	def updateLastTrialFig(self):
		
		dT=np.divide(1,int(self.sesVarD['sRate']))
		posPltYData=np.array(psData.aOut1)
		posPltYData2=np.array(psData.aOut1)
		self.lastAx.set_xlim([0,int(self.sesVarD['tDur'])*int(self.sesVarD['sRate'])])
		self.curReadAx.set_xlim([0,int(self.sesVarD['tDur'])*int(self.sesVarD['sRate'])])

		x0=np.array(psData.tm)    

		self.last_aIn1.set_xdata(x0)
		self.last_aIn1.set_ydata(posPltYData)
		self.last_aIn2.set_xdata(x0)
		self.last_aIn2.set_ydata(posPltYData2)
		self.lastAx.draw_artist(self.last_aIn1)
		self.lastAx.draw_artist(self.last_aIn2)
		self.lastAx.draw_artist(self.lastAx.patch)

		self.trialFig.canvas.draw_idle()

		self.trialFig.canvas.flush_events()

class psUtil:

	def getFilePath(self):

		self.selectPath = fd.askopenfilename(title =\
			"what what?",defaultextension='.csv')

	def setSessionPath(self):
		dirPathFlg=os.path.isdir(self.dirPath_tv.get())
		if dirPathFlg==False:
			os.mkdir(self.dirPath_tv)
		self.sesVarD['dirPath']=self.dirPath_tv.get()
		
		self.setSesPath=1
		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')

	def mapAssign(self,l1,l2):
		for x in range(0,len(l1)):
			try:
				l2[x]=float(l2[x])
				if l2[x].is_integer():
					l2[x]=int(l2[x])
					exec('self.{}=int({})'.format(l1[x],l2[x]))
				elif l2[x].is_integer()==0:
					exec('self.{}=float({})'.format(l1[x],l2[x]))
			except:
				exec('self.{}=({})'.format(l1[x],l2[x]))

	def mapAssignStringEntries(self,l1,l2,):
		for x in range(0,len(l1)):
			a=[l2[x]]
			
			
			exec('self.{}.set(a[0])'.format(l1[x]))
			
	def refreshDictFromGui(self,dictString):
		
		# dict string is the base string name of your dict.

		dictName=eval('self.{}'.format(dictString)) #like a pointer
	
		
		for key in list(dictName.keys()):
			try:
				# we need to append all TVs with their dict name
				a=eval('self.{}_{}_tv.get()'.format(dictString,key))
				try:
					a=float(a)
					if a.is_integer():
						a=int(a)
					exec('dictName["{}"]={}'.format(key,a))
					
				except:
					try:
						exec('dictName["{}"]="{}"'.format(key,a))
						
					except:
						1	
			except:
				a=1+1

	def refreshGuiFromDict(self,dictName):

		for key in list(dictName.keys()):
			try:
				eval('self.{}_tv.set(dictName["{}"])'.format(key,key))
			except:
				a=1+1

	def exportAnimalMeta(self):

		psUtil.refreshSubDirs(self)
		psUtil.refreshDictFromGui(self,"sesVarD")
		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')
		
		self.sesVarD_Bindings.to_csv('{}{}_sesVarD{}.csv'.\
			format(self.sesDataPath,self.sesVarD['animalID'],\
				int(self.sesVarD['currentSession'])))
		
		self.sesVarD_Bindings.to_csv('{}sesVarD.csv'.format(self.sesVarD['dirPath'] + "/" ))

	def mwLoadOutputsBtn(self):
		aa=fd.askopenfilename(title = "what what?",defaultextension='.csv')
		tempMeta=pd.read_csv(aa,index_col=0)
		aa=tempMeta.dtypes.index
		varNames=[]
		varVals=[]
		for x in range(0,len(tempMeta.columns)):
			varNames.append(aa[x])
			varVals.append(tempMeta.iloc[0][x])
		
		psUtil.mapAssignStringEntries(self,varNames,varVals)

	def refreshSubDirs(self):
		self.sesVarD['dirPath']=self.selectPath + '/'
		tempDirTS=datetime.datetime.fromtimestamp(time.time()).strftime('%m%d%Y')
		self.todaySubPath=self.selectPath + '/' + tempDirTS


		self.sesDataPath=self.todaySubPath + '/' + "sessionData" + '/'
		self.trialDataPath=self.todaySubPath + '/' + "trialData" + '/'
		if os.path.exists(self.todaySubPath)==0:
			os.mkdir(self.todaySubPath)
		if os.path.exists(self.trialDataPath)==0:
			os.mkdir(self.trialDataPath)
		if os.path.exists(self.sesDataPath)==0:
			os.mkdir(self.sesDataPath)

class psWindow:

	def psWindowPopulate(self):

		self.master.title("pyStim")
		self.col2BW=10
		
		pStart=0
		serStart=pStart+3
		sesStart=serStart+8
		plotStart=sesStart+11
		mainStart=plotStart+6

		psWindow.addSerialBlock(self,serStart)
		psWindow.addSessionBlock(self,sesStart)
		psWindow.addPlotBlock(self,plotStart)
		psWindow.addMainBlock(self,mainStart)

	def addMainBlock(self,startRow):
		self.startRow = startRow
		self.blankLine(self.master,startRow)

		self.blankLine(self.master,startRow+1)

		self.mainCntrlLabel = Label(self.master, text="Main Controls")\
		.grid(row=startRow,column=0,sticky=W)

		self.quitBtn = Button(self.master,text="Exit Program",command = \
			lambda: psWindow.mwQuitBtn(self), width=self.col2BW)
		self.quitBtn.grid(row=startRow+1, column=2)

		self.startBtn = Button(self.master, text="Start Task",width=10,command=\
			lambda: pyStim.runStimSession(self) ,state=NORMAL)
		self.startBtn.grid(row=startRow+1, column=0,sticky=W,padx=10)

		self.endBtn = Button(self.master, text="End Task",width=self.col2BW, \
			command=lambda:pdState.switchState(self,self.stMapD['endState']),state=DISABLED)
		self.endBtn.grid(row=startRow+2, column=0,sticky=W,padx=10)

	def addSessionBlock(self,startRow):
		# @@@@@ --> Session Block
		self.sesPathFuzzy=1 # This variable is set when we guess the path.

		self.animalID=self.sesVarD['animalID']
		self.dateStr = datetime.datetime.fromtimestamp(time.time()).\
		strftime('%H:%M (%m/%d/%Y)')

		self.blankLine(self.master,startRow)
		self.sessionStuffLabel = Label(self.master,text="Session Stuff ",justify=LEFT).\
		grid(row=startRow+1, column=0,sticky=W)

		self.timeDisp = Label(self.master, text=' #{} started: '\
			.format(int(self.sesVarD['currentSession'])) + self.dateStr,justify=LEFT)
		self.timeDisp.grid(row=startRow+2,column=0,sticky=W)

		self.dirPath_tv=StringVar(self.master)
		self.pathEntry=Entry(self.master,textvariable=self.dirPath_tv,width=24,bg='grey')
		self.pathEntry.grid(row=startRow+3,column=0,sticky=W)
		self.dirPath_tv.set(os.path.join(os.getcwd(),self.sesVarD['animalID']))

		self.setPath_button = Button(self.master,text="<- Set Path",\
			command=lambda:psWindow.mwPathBtn(self),width=self.col2BW)
		self.setPath_button.grid(row=startRow+3,column=2)

		self.aIDLabel=Label(self.master, text="animal id:")\
		.grid(row=startRow+4,column=0,sticky=W)
		self.animalID_tv=StringVar(self.master)
		self.animalIDEntry=Entry(self.master,textvariable=\
			self.animalID_tv,width=14,bg='grey')
		self.animalIDEntry.grid(row=startRow+4,column=0,sticky=E)
		self.animalID_tv.set(self.sesVarD['animalID'])

		self.totalTrials_label = Label(self.master,text="total trials:")\
		.grid(row=startRow+5,column=0,sticky=W)
		self.totalTrials_tv=StringVar(self.master)
		self.totalTrials_tv.set('100')
		self.totalTrials_entry=Entry(self.master,textvariable=\
			self.totalTrials_tv,width=10).\
		grid(row=startRow+5,column=0,sticky=E)

		self.curSession_label = Label(self.master,text="current session:").\
		grid(row=startRow+6,column=0,sticky=W)
		self.currentSession_tv=StringVar(self.master)
		self.currentSession_tv.set(str(self.sesVarD['currentSession']))
		self.curSession_entry=Entry(self.master,textvariable=\
			self.currentSession_tv,width=10)
		self.curSession_entry.grid(row=startRow+6,column=0,sticky=E)

		self.tDur_label = Label(self.master,text=" trial dur:")\
		.grid(row=startRow+7,column=0,sticky=W)
		self.tDur_tv=StringVar(self.master)
		self.tDur_tv.set('5')
		self.tDur_entry=Entry(self.master,textvariable=\
			self.tDur_tv,width=10).\
		grid(row=startRow+7,column=0,sticky=E)

		self.cntrFreqA_label = Label(self.master,text=" cntrFreqA:")\
		.grid(row=startRow+8,column=0,sticky=W)
		self.cntrFreqA_tv=StringVar(self.master)
		self.cntrFreqA_tv.set('0')
		self.cntrFreqA_entry=Entry(self.master,textvariable=\
			self.cntrFreqA_tv,width=10).\
		grid(row=startRow+8,column=0,sticky=E)

		self.cntrFreqB_label = Label(self.master,text=" cntrFreqB:")\
		.grid(row=startRow+9,column=0,sticky=W)
		self.cntrFreqB_tv=StringVar(self.master)
		self.cntrFreqB_tv.set('0')
		self.cntrFreqB_entry=Entry(self.master,textvariable=\
			self.cntrFreqB_tv,width=10).\
		grid(row=startRow+9,column=0,sticky=E)

		

		self.taskProbsBtn = Button(self.master,text='Output Vars',\
			width=self.col2BW,command=self.taskProbWindow)
		self.taskProbsBtn.grid(row=startRow+4, column=2)
		self.taskProbsBtn.config(state=NORMAL)

		self.loadAnimalMetaBtn = Button(self.master,text = 'Load Metadata',\
			width = self.col2BW,command = lambda: psWindow.mwLoadMetaBtn(self,1))
		self.loadAnimalMetaBtn.grid(row=startRow+1, column=2)
		self.loadAnimalMetaBtn.config(state=NORMAL)

		self.saveCurrentMetaBtn=Button(self.master,text="Save Cur. Meta",\
			command=lambda:psUtil.exportAnimalMeta(self), width=self.col2BW)
		self.saveCurrentMetaBtn.grid(row=startRow+2,column=2)

		self.useCSV=BooleanVar(self.master)
		self.useCSV.set(0)
		self.useCSVToggle=Checkbutton(self.master, \
			text="Use CSV",variable=self.useCSV,command=lambda: psWindow.useCSVToggle_CB(self))
		self.useCSVToggle.grid(row=startRow+6, \
			column=2,sticky=W,padx=5)
		self.useCSVToggle.deselect()
		self.useCSVToggle.config(state=DISABLED)

		self.loopCSV=BooleanVar(self.master)
		self.loopCSV.set(0)
		self.loopCSVToggle=Checkbutton(self.master, \
			text="Loop CSV",variable=self.loopCSV,command=lambda: psWindow.useCSVToggle_CB(self))
		self.loopCSVToggle.grid(row=startRow+7, \
			column=2,sticky=W,padx=5)
		self.loopCSVToggle.deselect()
		self.loopCSVToggle.config(state=DISABLED)

	def useCSVToggle_CB(self):
		if self.useCSV.get()==1:
			tShp=self.ptVarD_chan1_pandaFrame.shape
			self.loadedTrials=tShp[1]
			self.sesVarD["totalTrials"]=self.loadedTrials
			psUtil.refreshGuiFromDict(self,self.sesVarD)

	def addSerialBlock(self,startRow):
		
		self.startRow = startRow
		self.blankLine(self.master,startRow)
		# @@@@@ --> Serial Block
		self.comPathLabel = Label(self.master,text="COM Port Location:",justify=LEFT)
		self.comPathLabel.grid(row=startRow,column=0,sticky=W)

		self.comPath_tv=StringVar(self.master)
		self.comPathEntry=Entry(self.master,textvariable=self.comPath_tv)
		self.comPathEntry.grid(row=startRow+1, column=0)
		self.comPathEntry.config(width=24)
		
		if sys.platform == 'darwin':
			self.comPath_tv.set(self.sesVarD['comPath'])
		elif sys.platform == 'win':
			self.comPath_tv.set('COM11')

		self.baudEntry_label = Label(\
			self.master,text="BAUD Rate:",justify=LEFT)
		self.baudEntry_label.grid(row=startRow+2, column=0,sticky=W)

		self.baudSelected=IntVar(self.master)
		self.baudSelected.set(self.sesVarD['baudRate'])
		self.baudPick = OptionMenu(self.master,\
			self.baudSelected,115200,19200,9600)
		self.baudPick.grid(row=startRow+2, column=0,sticky=E)
		self.baudPick.config(width=14)

	def addPlotBlock(self,startRow):
		self.blankLine(self.master,startRow)
		self.plotBlock_label = Label(self.master,text="Plotting")
		self.plotBlock_label.grid(row=startRow+1, column=0,sticky=W)
		
		self.sampsToPlot_label = Label(self.master,text="samples per plot:")
		self.sampsToPlot_label.grid(row=startRow+2,column=0,sticky=W)
		self.sampsToPlot_tv=StringVar(self.master)
		self.sampsToPlot_entry=Entry(self.master,width=5,textvariable=\
			self.sampsToPlot_tv)
		self.sampsToPlot_entry.grid(row=startRow+2, column=0,sticky=E)
		self.sampsToPlot_tv.set(str(self.sesVarD['sampsToPlot']))

		self.uiUpdateSamps_label = Label(self.master, text="samples / UI update:")
		self.uiUpdateSamps_label.grid(row=startRow+3, column=0,sticky=W)
		self.uiUpdateSamps_tv=StringVar(self.master)
		self.uiUpdateSamps_entry=Entry(self.master,width=5,textvariable=\
			self.uiUpdateSamps_tv)
		self.uiUpdateSamps_entry.grid(row=startRow+3, column=0,sticky=E)
		self.uiUpdateSamps_tv.set(str(self.sesVarD['uiUpdateSamps']))

		self.sRate_label = Label(self.master, text="teensy rate:")
		self.sRate_label.grid(row=startRow+4, column=0,sticky=W)
		self.sRate_tv=StringVar(self.master)
		self.sRate_entry=Entry(self.master,width=5,textvariable=self.sRate_tv)
		self.sRate_entry.grid(row=startRow+4, column=0,sticky=E)
		self.sRate_tv.set(str(self.sesVarD['sRate']))


		self.togglePlotWinBtn=Button(self.master,text = 'Toggle Plot',\
			width=self.col2BW,\
			command=lambda:psPlot.trialPlotFig(self))
		self.togglePlotWinBtn.grid(row=startRow+2, column=2)
		self.togglePlotWinBtn.config(state=NORMAL)

	def mwPathBtn(self):
		
		# 1 Get the path, or assume root.
		try:
			self.selectPath = fd.askdirectory(title ="what what?")
			
		except:
			self.selectPath='/'
			
		self.dirPath_tv.set(self.selectPath)
		self.pathEntry.config(bg='white')
		self.animalID_tv.set(os.path.basename(self.selectPath))
		self.sesVarD['animalID']=self.animalID_tv.get()
		self.animalIDEntry.config(bg='white')
		self.sesPathFuzzy=0

		sesString='{}sesVarD.csv'.format(self.selectPath + '/')
		ch0String='{}ptVarD_chan0.csv'.format(self.selectPath + '/')
		ch1String='{}ptVarD_chan1.csv'.format(self.selectPath + '/')
		
		self.loadedSesVarD=os.path.isfile(sesString)  
		self.loadedCh0=os.path.isfile(ch0String)
		self.loadedCh1=os.path.isfile(ch1String)
		
		if self.loadedSesVarD:

			psVariables.loadMeta(self,1,sesString)
			psVariables.pandasToDict(self,self.sesVarD_pandaFrame,self.sesVarD,1)
			psUtil.refreshGuiFromDict(self,self.sesVarD)
		
		if self.loadedCh0 is True:
			
			psVariables.loadMeta(self,1,ch0String)
			psVariables.pandasToDict(self,self.ptVarD_chan0_pandaFrame,self.ptVarD_chan0,1)
			psUtil.refreshGuiFromDict(self,self.ptVarD_chan0)

		if self.loadedCh1 is True:

			psVariables.loadMeta(self,1,ch1String)
			psVariables.pandasToDict(self,self.ptVarD_chan1_pandaFrame,self.ptVarD_chan1,1)
			psUtil.refreshGuiFromDict(self,self.ptVarD_chan1)
			self.useCSVToggle.config(state=NORMAL)
			self.loopCSVToggle.config(state=NORMAL)
			

		
		psUtil.refreshSubDirs(self)
		# psVariables.dictToPandas(self,self.sesVarD,'sesVarD')
		psUtil.setSessionPath(self)

	def mwLoadMetaBtn(self,dCol):

		# 1) Get the path to a CSV. 
		# Format of CSV is C0,R0 = Dict Name
		# C0,R1->N Variable names
		# C1->N Variable Values
		
		aa=fd.askopenfilename(title = "what what?",defaultextension='.csv')
		bb=os.path.basename(aa)
		cc=bb.split('.')

		tempMeta=pd.read_csv(aa,index_col=0,header=None)
		gg=tempMeta.index		
		dictName='self.' + cc[0]
		exec('self.{}_pandaFrame=tempMeta'.format(cc[0]))

		for x in range(0,len(gg)):
			try:
				a=tempMeta.iloc[x][dCol]
				tKey=gg[x]

				try:
					a=float(a)
					if a.is_integer():
						a=int(a)
					exec('{}["{}"]={}'.format(dictName,tKey,a))

				except:
					try:
						exec('{}["{}"]="{}"'.format(dictName,tKey,a))
						
					except:
						1

			except:
				a=1+1

	def mwQuitBtn(self):

		exit()

class pyStim:

	def __init__(self,master):
		
		psData.initSessionData(self)
		psVariables.setSessionVars(self,'sesVarD')

		# some of the session variables updates rely on time/sample conversions
		self.sesVarD['uiUpdateSamps']=\
		int(self.sesVarD['sRate']/self.sesVarD['fps']) # gives 30 fps
		self.sesVarD['sampsToPlot']=\
		int(self.sesVarD['sRate']*self.sesVarD['timeToPlot'])  
		
		# the last trial is either 0 on a cold start,
		# or X+1 where X is the last trial you ran.
		self.lastTrial=self.sesVarD['tNum']-1
		
		pyStim.configChans(self)
		pyStim.configChans(self)
		self.master = master
		self.frame = Frame(self.master)
		
		root.wm_geometry("+0+0")
		
		psWindow.psWindowPopulate(self)
		psPlot.trialPlotFig(self)

	def connectTeensy(self):

		baudRate=self.baudSelected.get()
		teensyPath=self.comPath_tv.get()
		self.teensy = serial.Serial(teensyPath,baudRate)
	
	def configChans(self):
		# todo: I enumerate here, to pave path for configurable channels.
		self.analogOutChannels='chan0','chan1'
		for x in range(0,len(self.analogOutChannels)):
			eval('psVariables.setPulseTrainVars(self, "{}")'.\
				format('ptVarD_' +\
			 self.analogOutChannels[x]))
	
	def runStimSession(self):

		pyStim.configChans(self)
		psData.initTrialData(self)
		
		self.sesVarD['totalTrials']=int(self.totalTrials_tv.get())
		self.sesVarD['currentSession']=int(self.currentSession_tv.get())+1
		self.currentSession_tv.set('{}'.format(int(self.sesVarD['currentSession'])))

		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')
		self.lastTrial=int(self.sesVarD['tNum'])
		
		pyStim.connectTeensy(self)
		tC=1
		lC=1
		while (int(self.sesVarD['tNum'])-self.lastTrial)<int(self.sesVarD['totalTrials']):
			if self.loadedCh0:
				if self.useCSV.get():
					psVariables.pandasToDict(self,self.ptVarD_chan0_pandaFrame,self.ptVarD_chan0,tC)
					pyStim.taskProbRefreshBtnCB(self)
				
			if self.loadedCh1:
				if self.useCSV.get():
					psVariables.pandasToDict(self,self.ptVarD_chan1_pandaFrame,self.ptVarD_chan1,tC)
					pyStim.taskProbRefreshBtnCB(self)
			
			tC=tC+1
			
			if self.loopCSV.get():
				if tC>self.loadedTrials:
					tC=1
			

			self.initPulseTrain()
			self.pulseTrainTrial()
			pyStim.saveTrialData(self)
			pyStim.updateSessionData(self)
			self.sesVarD['tDur']=int(self.tDur_tv.get())
			self.sesVarD['cntrFreqA']=int(self.cntrFreqA_tv.get())
			self.sesVarD['cntrFreqB']=int(self.cntrFreqB_tv.get())
			self.sesVarD['tNum']=int(self.sesVarD['tNum'])+1
			self.sesVarD['totalTrials']=int(self.totalTrials_tv.get())
			self.sesVarD['uiUpdateSamps']=int(self.uiUpdateSamps_tv.get())
			self.sesVarD['sampsToPlot']=int(self.sampsToPlot_tv.get())

		self.teensy.close()
		pyStim.saveSessionData(self)
		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')

	def cleanup(self):
		
		self.teensy.close()

	def readSerialData(self,comObj,headerString,headerCount):

		sR=comObj.readline().strip().decode()
		sR=sR.split(',')

		if len(sR)==headerCount and sR[0]==headerString:
			newData=1
		else:
			newData=0
		return sR,newData

	def saveTrialData(self):
		self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).strftime('%H%M_%m%d%Y')
		tCo=[]
		for x in range(0,len(psData.trialStores)):
			tCo=eval('psData.{}'.format(psData.trialStores[x]))
			if x==0:
				rf=pd.DataFrame({'{}'.format(psData.trialStores[x]):tCo})
			elif x != 0:
				tf=pd.DataFrame({'{}'.format(psData.trialStores[x]):tCo})
				rf=pd.concat([rf,tf],axis=1)

		psUtil.refreshSubDirs(self)


		rf.to_csv('{}{}_{}_s{}_trial_{}.csv'.\
			format(self.trialDataPath,self.sesVarD['animalID'],self.dateSvStr,\
			 int(self.sesVarD['currentSession']),int(self.sesVarD['tNum'])))
		self.trialDataExists=0

	def updateSessionData(self):

		psData.trialNumber.append(int(self.sesVarD['tNum']))
		psData.trialTime.append(psData.tm[-1])
		# psData.preTime.append(psData.tC[0])
		psData.stimType.append(self.s)
		psData.trialDuration.append(int(self.sesVarD['tDur']*self.sesVarD['sRate']))
		psData.stimAmp_ChanA.append((self.ptVarD_chan0['pulseAmpV']/3.3)*4095)
		psData.stimAmp_ChanB.append((self.ptVarD_chan1['pulseAmpV']/3.3)*4095)

	def saveSessionData(self):
		self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).\
		strftime('%H%M_%m%d%Y')

		tCo=[]
		for x in range(0,len(psData.sessionStores)):
			tCo=eval('psData.{}'.format(psData.sessionStores[x]))
			if x==0:
				rf=pd.DataFrame({'psData.{}'.\
					format(psData.sessionStores[x]):tCo})
			elif x != 0:
				tf=pd.DataFrame({'psData.{}'.\
					format(psData.sessionStores[x]):tCo})
				rf=pd.concat([rf,tf],axis=1)

		psUtil.refreshSubDirs(self)
		rf.to_csv('{}{}_{}_s{}_sessionData.csv'.\
			format(self.sesDataPath,self.sesVarD['animalID'],self.dateSvStr,\
			 int(self.sesVarD['currentSession'])))
		self.sessionDataExists=0

		psUtil.exportAnimalMeta(self)

	def updatePlotCheck(self):
		
		# uncoment below to lock the GUI
		# psVariables.setSessionVars(self,'sesVarD')
		
		if plt.fignum_exists(100):
			psPlot.updateTrialFig(self)
		self.cycleCount=0

	def initPulseTrain(self):
		
		psUtil.refreshDictFromGui(self,"sesVarD")
		psUtil.refreshDictFromGui(self,"ptVarD_chan0")
		psUtil.refreshDictFromGui(self,"ptVarD_chan1")

		self.inTrial=1
		self.s=-1
		psData.initTeensyStateData(self)
		psData.initTrialData(self)
		
		self.sNum=int(self.sesVarD['sNum'])
		
		self.varNums=psData.varNums
		self.varNames=psData.varNames
		self.varHeader=psData.varHeader

		self.varCount=int(self.sesVarD['varCount'])
		self.dataCount=int(self.sesVarD['dataCount'])

		
		self.current_milli_time = lambda: int(round(time.time() * 1000))
		self.initT=self.current_milli_time();
		
		self.resetVariables=0
		self.rxBit=0
		self.txBit=0

	def blankLine(self,targ,startRow):
		self.guiBuf=Label(targ, text="")
		self.guiBuf.grid(row=startRow,column=0,sticky=W)

	def taskProbWindow(self):
		tb_frame = Toplevel()
		tb_frame.title('Output Vars')
		self.tb_frame=tb_frame
		self.populateVarFrameFromDict(self.\
			ptVarD_chan0,0,0,'ptVarD_chan0','tb_frame')
		self.populateVarFrameFromDict(self.\
			ptVarD_chan1,2,0,'ptVarD_chan1','tb_frame')

	def taskProbRefreshBtnCB(self):
		try:
			self.populateVarFrameFromDict(self.\
				ptVarD_chan0,0,0,'ptVarD_chan0','tb_frame')
			self.populateVarFrameFromDict(self.\
				ptVarD_chan1,2,0,'ptVarD_chan1','tb_frame')
		except:
			1

	def populateVarFrameFromDict(self,dictName,stCol,varPerCol,headerString,frameName):
		rowC=2
		stBCol=stCol+1
		spillCount=0
		exec('r_label = Label(self.{}, text="{}",justify=LEFT)'.format(frameName,headerString))
		exec('r_label.grid(row=1,column=stCol)'.format(dictName))
		for key in list(dictName.keys()):
			if varPerCol != 0:
				if (rowC % varPerCol)==0:
					rowC=2
					spillCount=spillCount+1
					stCol=stCol+(spillCount+1)
					stBCol=stCol+(spillCount+2)
			
			exec('self.{}_tv=StringVar(self.{})'.format(headerString + "_" + key,frameName))
			exec('self.{}_label = Label(self.{}, text="{}")'.\
				format(headerString + "_" + key,frameName,key))
			exec('self.{}_entries=Entry(self.{},width=5,textvariable=self.{}_tv)'.\
				format(headerString + "_" + key,frameName, headerString + "_"  + key))
			exec('self.{}_label.grid(row={},column=stBCol)'.format(headerString + "_" + key,rowC))
			exec('self.{}_entries.grid(row={},column=stCol)'.format(headerString + "_" + key,rowC))
			exec('self.{}_tv.set({})'.format(headerString + "_"  + key,dictName[key]))
			rowC=rowC+1

	def pulseTrainTrial(self):
		self.dumpPlot=0
		waitSamps=30*int(self.sesVarD['sRate'])
		while self.inTrial ==1:
			# handshake with teensy. we start in -1, but want to go to 0
			if self.s==-1:
				self.inTrial=1
				
				# tell teensy to go to 0.
				if self.txBit==0:
					self.teensy.write('a0>'.encode('utf-8'))
					waitCount=0
					self.txBit=1

				elif self.txBit==1:
					waitCount=waitCount+1
					
					self.tR,self.rxBit=self.readSerialData(self.teensy,'vars',self.varCount)
					

					if self.rxBit:
						sentState=int(self.tR[self.sNum])
						if sentState == 0:
							initSt=0  # debug
							self.txBit=0
							self.rxBit=0
							self.s=sentState

						elif sentState != 0:
							self.txBit=0

					elif self.rxBit==0 and waitCount>waitSamps:
						self.txBit=0

			elif self.s==0:

				if initSt==0:					
					n=1
					tDur=int(self.sesVarD['tDur']*self.sesVarD['sRate'])
					
					pAmpA=(self.ptVarD_chan0['pulseAmpV']/3.3)*4095
					pDurA=self.ptVarD_chan0['pulseTime']*int(self.sesVarD['sRate'])
					iPIntA=self.ptVarD_chan0['dwellTime']*int(self.sesVarD['sRate'])
					nPulsesA=self.ptVarD_chan0['nPulses']
					bDurA=self.ptVarD_chan0['baselineTime']*int(self.sesVarD['sRate'])

					pAmpB=(self.ptVarD_chan1['pulseAmpV']/3.3)*4095
					pDurB=self.ptVarD_chan1['pulseTime']*int(self.sesVarD['sRate'])
					iPIntB=self.ptVarD_chan1['dwellTime']*int(self.sesVarD['sRate'])
					nPulsesB=self.ptVarD_chan1['nPulses']
					bDurB=self.ptVarD_chan1['baselineTime']*int(self.sesVarD['sRate'])

					cntrFreqA=self.sesVarD['cntrFreqA']
					cntrFreqB=self.sesVarD['cntrFreqB']
					pST=self.current_milli_time()
					self.varsSent=0
					self.resetVariables=1
					initSt=1					


				if self.txBit==0:
					self.teensy.write('a1>'.encode('utf-8'))
					waitCount=0
					self.txBit=1

				elif self.txBit==1:
					waitCount=waitCount+1
					self.tR,self.rxBit=self.readSerialData(self.teensy,'vars',self.varCount)
					

					if self.rxBit:
						sentState=int(self.tR[self.sNum])
						if sentState == 1:
							initSt=0  # debug
							self.txBit=0
							self.rxBit=0
							self.s=sentState
						
						elif sentState != 1:
							self.txBit=0

					elif self.rxBit==0 and waitCount>waitSamps:
						self.txBit=0
			
			elif self.s == 1:
				
				if initSt==0:

					initSt=1
				
				if self.varsSent==0:
					
					if self.txBit==0:
						varCheck=[]
						
						for x in range(1,len(self.tR)):
							
							curVarTmp=int(self.tR[x])
							if curVarTmp == -1:
								varCheck.append(x)

						if len(varCheck)>0:
							upVar=varCheck[0]
							tHead=self.varHeader[upVar]
							tVal=str(int(eval('{}'.format(psData.varNames[upVar]))))
							tHead=psData.varHeader[upVar]
							self.teensy.write('{}{}>'.format(tHead,tVal).encode('utf-8'))
							
							self.txBit=1
							waitCount=0
							pyStim.updatePlotCheck(self)

						if len(varCheck)==0:
							self.varsSent=1
							doneOnce=0

					elif self.txBit==1:
						waitCount=waitCount+1
						self.tR,self.rxBit=self.readSerialData(self.teensy,'vars',self.varCount)
						if self.rxBit:
							self.txBit=0
							pyStim.updatePlotCheck(self)

						elif self.rxBit==0 and waitCount>waitSamps:
							self.txBit=0

				elif self.varsSent==1 and doneOnce==0:
					self.collecting=1
					initSt=0
					self.txBit=0
					self.rxBit=0
					self.teensy.write('a2>'.encode('utf-8'))
					self.s=2


			elif self.s==2:
				while self.collecting:
					dR,dU=self.readSerialData(self.teensy,'data',self.dataCount)
					if dU:
						n=n+1
						if n % int(self.sesVarD['uiUpdateSamps']) == 0:
							pyStim.updatePlotCheck(self)
						for x in range(0,len(psData.trialStores)):
							a=(dR[psData.trialStoresIDs[x]])
							exec('psData.{}.append({})'.format(psData.trialStores[x],a))
						if n % int(self.sesVarD['uiUpdateSamps']) == 0:
							pyStim.updatePlotCheck(self)
						if psData.pS[-1]==0 or n>=int(self.sesVarD['tDur'])*int(self.sesVarD['sRate']):
							self.collecting=0
							n=0
							
				
				while self.collecting==0:
					
					while self.teensy.in_waiting>0:
						n=n+1
						if n % int(self.sesVarD['uiUpdateSamps']) == 0:
							pyStim.updatePlotCheck(self)
							self.dumpPlot=1
						dR,dU=self.readSerialData(self.teensy,'data',self.dataCount)
						if dU:
							for x in range(0,len(psData.trialStores)):
								a=(dR[psData.trialStoresIDs[x]])
								exec('psData.{}.append({})'.format(psData.trialStores[x],a))


					if initSt==0:
						psPlot.updateLastTrialFig(self)
						initSt=1
						

					self.teensy.write('a0>'.encode('utf-8'))
					self.inTrial ==0
					return()
		

root = Tk()
app = pyStim(root)
root.mainloop()
exit()