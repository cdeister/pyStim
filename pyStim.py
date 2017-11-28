# pyStim v0.98
# _________________
# Works with microcontrollers that have hardward DACs, like the Teensy 3 line.
# It is intended to be used with a Teensy3.5/3.6, both of which have 2 analog outs.
#
# You need to load 'teensyStim.ino' onto your teensy (or cortex MC).

# Chris Deister - cdeister@brown.edu
# Anything that is licenseable is governed by an MIT License in the github directory. 


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

class psVariables:

	def setSessionVars(self,idString):
		sesVarD = {'currentSession':1,'dirPath':"/",\
		'animalID':"an1",'totalTrials':5,'uiUpdateSamps':250,'sRate':1000,\
		'sampsToPlot':5000,'comBoard':2762721,\
		'baudRate':115200,'dacMaxVal':3.3,'dacMinVal':0,'adcBitDepth':8,\
		'dacBitDepth':12,'varCount':13,'sNum':1,'dataCount':8,\
		'serDelay':0.000001,'tNum':1,'tDur':2,'sessionNumber':1}

		# dynamic
		sesVarD['uiUpdateSamps']=int(sesVarD['sRate']/20)
		sesVarD['sampsToPlot']=int(sesVarD['sRate']*1)
		
		exec('self.{}=sesVarD'.format(idString))
		# self.sesVarD['dirPath']
		psVariables.dictToPandas(self,sesVarD,idString)


	def setPulseTrainVars(self,idString):

		ptVarD = {'dwellTime':0.005,'pulseTime':0.01,'nPulses':20,\
		'pulseAmpV':3.3,'baselineTime':0.5}
		exec('self.{}=ptVarD'.format(idString))

		psVariables.dictToPandas(self,ptVarD,idString)

	def dictToPandas(self,dictName,idString):

		tLab=[]
		tVal=[]
		for key in list(dictName.keys()):
			tLab.append(key)
			tVal.append(dictName[key])
		exec('self.{}_Bindings=pd.Series(tVal,index=tLab)'.format(idString))

	def pandasToDict(self,pdName,dictName):
		varIt=0
		for k in list(pdName.index):
			a=pdName[varIt]
			dictName[k]=a
			varIt=varIt+1

class psData:

	def initSessionData(self):
		psData.sessionStores='trialNumber','trialTime','preTime','stimType','trialDuration','stimAmp_ChanA','stimAmp_ChanB'
		for x in range(0,len(psData.sessionStores)):
			exec('psData.{}=[]'.format(psData.sessionStores[x]))

	def initTrialData(self):
		psData.trialStores='tm','v1','v2','rv1','rv2','tC','pS'
		psData.trialStoresIDs=[1,2,3,4,5,6,7]
		for x in range(0,len(psData.trialStores)): 
			exec('psData.{}=[]'.format(psData.trialStores[x]))


	def initTeensyStateData(self): # hacky

		psData.varHeader='','a','b','c','d','e','f','g','h','i','j','k','l'	
		psData.varNames='head','state','pDurA','iPIntA','pAmpA','nPulsesA','bDurA',\
		'pDurB','iPIntB','pAmpB','nPulsesB','bDurB','tDur'
		psData.varNums=[0,1,2,3,4,5,6,7,8,9,10,11,12]

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
		# dT=np.divide(1,self.sesVarD['sRate'])
		plt.style.use('dark_background')
		self.trialFramePosition='+370+0' # can be specified elsewhere
		self.updateTrialAxes=0
		
		self.trialFig = plt.figure(100,figsize=(4,5), dpi=100)
		tNum=int(self.sesVarD['tNum'])-(self.lastTrial)
		self.trialFig.suptitle('trial # {} of {}'.format(tNum,int(self.sesVarD['totalTrials'])),fontsize=10)
		self.trialFig.subplots_adjust(wspace=0.1,hspace=0.2)
		
		mng = plt.get_current_fig_manager()
		eval('mng.window.wm_geometry("{}")'.format(self.trialFramePosition))
		self.positionAxes=plt.subplot2grid([2,2],(0,0),colspan=2,rowspan=1)
		self.positionAxes.set_yticks([])
		self.positionAxes.set_xticks([])
		self.positionAxes.set_ylim([-100,4200])
		self.positionAxes.set_xlim([0,int(self.sesVarD['tDur'])*int(self.sesVarD['sRate'])])
		self.positionAxes.set_title('current trial',fontsize=10)
		self.positionLine,=self.positionAxes.plot([1,1],color="olive",lw=1)
		self.positionLine2,=self.positionAxes.plot([1,1],color="cornflowerblue",lw=1)
		plt.show(block=False)

		self.lastTrialAxes=plt.subplot2grid([2,2],(1,0),colspan=2,rowspan=1)
		self.lastTrialAxes.set_yticks([])
		self.lastTrialAxes.set_ylim([-500,4500])
		self.lastTrialAxes.set_xlim([0,int(self.sesVarD['tDur'])*int(self.sesVarD['sRate'])])
		self.lastTrialAxes.set_title('last trial',fontsize=10)
		self.lastDataLine,=self.lastTrialAxes.plot([1,1],color="olive",lw=1)
		self.lastDataLine2,=self.lastTrialAxes.plot([1,1],color="cornflowerblue",lw=1)
		plt.show(block=False)

	
	def updateTrialFig(self):
		# dT=np.divide(1,self.sesVarD['sRate'])
		splt=int(self.sesVarD['sampsToPlot'])
		posPltYData=np.array(psData.v1[-int(splt):])
		posPltYData2=np.array(psData.v2[-int(splt):])
		x0=np.array(psData.tm[-int(splt):])
		# x1=np.multiply(x0,dT)
		# x0=[]
		tNum=(int(self.sesVarD['tNum'])+1)-(self.lastTrial)
		self.trialFig.suptitle('trial # {} of {}'.format(tNum,int(self.sesVarD['totalTrials'])),fontsize=10)
		
		if len(x0)>1:
			self.positionLine.set_xdata(x0)
			self.positionLine.set_ydata(posPltYData)
			self.positionLine2.set_xdata(x0)
			self.positionLine2.set_ydata(posPltYData2)
			self.positionAxes.draw_artist(self.positionLine)
			self.positionAxes.draw_artist(self.positionLine2)
			self.positionAxes.draw_artist(self.positionAxes.patch)

			self.trialFig.canvas.draw_idle()

		self.trialFig.canvas.flush_events()

	def updateLastTrialFig(self):
		
		dT=np.divide(1,int(self.sesVarD['sRate']))
		posPltYData=np.array(psData.v1)
		posPltYData2=np.array(psData.v2)

		x0=np.array(psData.tm)    
		# x1=np.multiply(x0,dT)
		# x0=[]

		self.lastDataLine.set_xdata(x0)
		self.lastDataLine.set_ydata(posPltYData)
		self.lastDataLine2.set_xdata(x0)
		self.lastDataLine2.set_ydata(posPltYData2)
		self.lastTrialAxes.draw_artist(self.lastDataLine)
		self.lastTrialAxes.draw_artist(self.lastDataLine2)
		self.lastTrialAxes.draw_artist(self.lastTrialAxes.patch)

		self.trialFig.canvas.draw_idle()

		self.trialFig.canvas.flush_events()

class psUtil:

	def getPath(self):

		self.selectPath = fd.askdirectory(title ="what what?")

	def getFilePath(self):

		self.selectPath = fd.askopenfilename(title ="what what?",defaultextension='.csv')

	def setSessionPath(self):
		dirPathFlg=os.path.isdir(self.dirPath_tv.get())
		if dirPathFlg==False:
			os.mkdir(self.dirPath_tv)
		self.sesVarD['dirPath']=self.dirPath_tv.get()
		print(self.sesVarD['dirPath'])
		self.setSesPath=1
		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')

	def mapAssign(self,l1,l2):
		for x in range(0,len(l1)):
			if type(l2[x])==int:
				exec('self.{}=int({})'.format(l1[x],l2[x])) 
			elif type(l2[x])==float:
				exec('self.{}=float({})'.format(l1[x],l2[x])) 

	def mapAssignStringEntries(self,l1,l2):
		for x in range(0,len(l1)):
			a=[l2[x]]
			print(a)
			print('db self.{}.set(a[0])'.format(l1[x]))
			exec('self.{}.set(a[0])'.format(l1[x]))
			print('db self.{}.set(a[0])'.format(l1[x]))

	def refreshDictFromGui(self,dictName):
		for key in list(dictName.keys()):
			a=eval('self.{}_tv.get()'.format(key))
			try:
				a=float(a)
				if a.is_integer():
					a=int(a)
				exec('dictName["{}"]={}'.format(key,a))
			except:
				exec('dictName["{}"]="{}"'.format(key,a))


	def refreshGuiFromDict(self,dictName):

		for key in list(dictName.keys()):
			eval('self.{}_tv.set(dictName["{}"])'.format(key,key))
			print('self.{}_tv.set(dictName["{}"])'.format(key,key))

	def exportAnimalMeta(self):
		try:
			tSavePath=self.sesDataPath + '/'
		except:
			tSavePath=self.dirPath_tv.get() + '/'

		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')
		self.sesVarD_Bindings.to_csv('{}{}_s{}_sesVars.csv'.\
			format(tSavePath,self.sesVarD['animalID'],int(self.sesVarD['currentSession'])))
		self.sesVarD_Bindings.to_csv('{}{}_sesVars.csv'.\
			format(tSavePath,self.sesVarD['animalID']))

	def mwLoadMetaBtn(self):
		aa=fd.askopenfilename(title = "what what?",defaultextension='.csv')
		tempMeta=pd.read_csv(aa,index_col=0)
		aa=tempMeta.dtypes.index
		print(aa)
		varNames=[]
		varVals=[]
		for x in range(0,len(tempMeta.columns)):
			varNames.append(aa[x])
			varVals.append(tempMeta.iloc[0][x])
		psUtil.mapAssignStringEntries(self,varNames,varVals)

class psWindow:

	def blankLine(self,targ,startRow):
		self.guiBuf=Label(targ, text="")
		self.guiBuf.grid(row=startRow,column=0,sticky=W)

	def mwQuitBtn(self):

		exit()

	def psWindowPopulate(self):

		self.master.title("pyStim")
		self.col2BW=10
		pStart=0
		sesStart=pStart+8
		mainStart=sesStart+7
		psWindow.addSessionBlock(self,sesStart)
		psWindow.addMainBlock(self,mainStart)

	def addMainBlock(self,startRow):
		self.startRow = startRow
		# psWindow.blankLine(self.master,startRow)

		self.mainCntrlLabel = Label(self.master, text="Main Controls:")\
		.grid(row=startRow,column=0,sticky=W)

		self.quitBtn = Button(self.master,text="Exit Program",command = \
			lambda: psWindow.mwQuitBtn(self), width=self.col2BW)
		self.quitBtn.grid(row=startRow+1, column=2)

		self.startBtn = Button(self.master, text="Start Task",width=10,command=\
			lambda: pyStim.runStimSession(self) ,state=NORMAL)
		self.startBtn.grid(row=startRow+1, column=0,sticky=W,padx=10)

		self.endBtn = Button(self.master, text="End Task",width=self.col2BW, \
			command=lambda:pdState.switchState(self,self.stMapD['endState']),state=NORMAL)
		self.endBtn.grid(row=startRow+2, column=0,sticky=W,padx=10)

	def addSessionBlock(self,startRow):
		# @@@@@ --> Session Block
		self.sesPathFuzzy=1 # This variable is set when we guess the path.

		self.animalID=self.sesVarD['animalID']
		self.dateStr = datetime.datetime.fromtimestamp(time.time()).\
		strftime('%H:%M (%m/%d/%Y)')

		# psWindow.blankLine(self.master,startRow)
		self.sessionStuffLabel = Label(self.master,text="Session Stuff: ",justify=LEFT).\
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



		self.loadAnimalMetaBtn = Button(self.master,text = 'Load Metadata',\
			width = self.col2BW,command = lambda: psWindow.mwLoadMetaBtn(self))
		self.loadAnimalMetaBtn.grid(row=startRow+1, column=2)
		self.loadAnimalMetaBtn.config(state=NORMAL)

		self.saveCurrentMetaBtn=Button(self.master,text="Save Cur. Meta",\
			command=lambda:psUtil.exportAnimalMeta(self), width=self.col2BW)
		self.saveCurrentMetaBtn.grid(row=startRow+2,column=2)

	def addSerialBlock(self,startRow):
		self.startRow = startRow

		# @@@@@ --> Serial Block
		self.comPathLabel = Label(self.master,text="COM Port Location:",justify=LEFT)
		self.comPathLabel.grid(row=startRow,column=0,sticky=W)

		self.comPath_tv=StringVar(self.master)
		self.comPathEntry=Entry(self.master,textvariable=self.comPath_tv)
		self.comPathEntry.grid(row=startRow+1, column=0)
		self.comPathEntry.config(width=24)
		
		if sys.platform == 'darwin':
			self.comPath_tv.set('/dev/cu.usbmodem2762721')
		elif sys.platform == 'win':
			self.comPath_tv.set('COM11')

		self.baudEntry_label = Label(\
			self.master,text="BAUD Rate:",justify=LEFT)
		self.baudEntry_label.grid(row=startRow+2, column=0,sticky=W)

		self.baudSelected=IntVar(self.master)
		self.baudSelected.set(115200)
		self.baudPick = OptionMenu(self.master,\
			self.baudSelected,115200,19200,9600)
		self.baudPick.grid(row=startRow+2, column=0,sticky=E)
		self.baudPick.config(width=14)

		self.createCom_button = Button(self.master,\
			text="Start Serial",width=self.col2BW, \
			command=lambda: pdSerial.serial_initComObj(self))
		self.createCom_button.grid(row=startRow+0, column=2)
		self.createCom_button.config(state=NORMAL)

		self.syncComObj_button = Button(self.master,\
			text="Sync Serial",width=self.col2BW, \
			command=lambda: pdSerial.syncSerial(self))
		self.syncComObj_button.grid(row=startRow+1, column=2)
		self.syncComObj_button.config(state=DISABLED)  

		self.closeComObj_button = Button(self.master,\
			text="Close Serial",width=self.col2BW, \
			command=lambda: pdSerial.serial_closeComObj(self))
		self.closeComObj_button.grid(row=startRow+2, column=2)
		self.closeComObj_button.config(state=DISABLED)

	def mwPathBtn(self):
		
		psUtil.getPath(self)
		self.dirPath_tv.set(self.selectPath)
		self.pathEntry.config(bg='white')
		self.animalID_tv.set(os.path.basename(self.selectPath))
		self.sesVarD['animalID']=self.animalID_tv.get()
		self.animalIDEntry.config(bg='white')
		self.sesPathFuzzy=0
		print('debug 1')

		sesString='{}{}_sesVars.csv'.format(self.selectPath + '/',self.animalID_tv.get())
		stMapString='{}{}_stateMap.csv'.format(self.selectPath + '/',self.animalID_tv.get())
		stVarString='{}{}_stateVars.csv'.format(self.selectPath + '/',self.animalID_tv.get())
		t1PString='{}{}_task1Probs.csv'.format(self.selectPath + '/',self.animalID_tv.get())
		t2PString='{}{}_task2Probs.csv'.format(self.selectPath + '/',self.animalID_tv.get())
		print('debug 2')

		self.loadedSesVars=os.path.isfile(sesString)  
		print(sesString)    
		self.loadedStates=os.path.isfile(stMapString)
		self.loadedStateVars=os.path.isfile(stVarString)
		self.loadedT1Probs=os.path.isfile(t1PString)
		self.loadedT2Probs=os.path.isfile(t2PString)
		print('hey')
		print(self.loadedSesVars)
		print('l')
		
		if self.loadedSesVars:
			print('debug GO')
			tempSesVar=pd.Series.from_csv(sesString)
			psVariables.pandasToDict(self,tempSesVar,self.sesVarD)
			psUtil.refreshGuiFromDict(self,self.sesVarD)

		if self.loadedStates is True:
			tempStMap=pd.Series.from_csv(stMapString)
			psVariables.pandasToDict(self,tempStMap,self.stMapD)
				
		if self.loadedStateVars is True:
			tempStateVars=pd.Series.from_csv(stVarString)
			psVariables.pandasToDict(self,tempStateVars,self.stVarD)
		
		if self.loadedT1Probs is True:
			tempT1Vars=pd.Series.from_csv(t1PString)
			psVariables.pandasToDict(self,tempT1Vars,self.task1D)
		
		if self.loadedT2Probs is True:
			tempT2Vars=pd.Series.from_csv(t2PString)
			psVariables.pandasToDict(self,tempT2Vars,self.task2D)

		tempDirTS=datetime.datetime.fromtimestamp(time.time()).strftime('%m%d%Y')
		self.todaySubPath=self.selectPath + '/' + tempDirTS
		self.sesDataPath=self.todaySubPath + '/' + "sessionData"
		self.trialDataPath=self.todaySubPath + '/' + "trialData"
		print(os.path.exists(self.todaySubPath))
		if os.path.exists(self.todaySubPath)==0:
			os.mkdir(self.todaySubPath)
		if os.path.exists(self.trialDataPath)==0:
			os.mkdir(self.trialDataPath)
		if os.path.exists(self.sesDataPath)==0:
			os.mkdir(self.sesDataPath)
		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')
		psUtil.setSessionPath(self)

	def mwLoadMetaBtn(self):
		aa=fd.askopenfilename(title = "what what?",defaultextension='.csv')
		tempMeta=pd.read_csv(aa,index_col=0)
		aa=tempMeta.dtypes.index
		varNames=[]
		varVals=[]
		print(varNames)
		for x in range(0,len(tempMeta.columns)):
			varNames.append(aa[x])
			varVals.append(tempMeta.iloc[0][x])
		psUtil.mapAssignStringEntries(self,varNames,varVals)

class psTypes:

	def yup(self):
		
		print('who')

class pyStim:

	def __init__(self,master):
		
		psData.initSessionData(self)
		psVariables.setSessionVars(self,'sesVarD')
		self.lastTrial=(int(self.sesVarD['tNum'])-1)
		print('debug: {}'.format(self.lastTrial))

		
		self.master = master
		self.frame = Frame(self.master)
		root.wm_geometry("+0+0")
		psWindow.psWindowPopulate(self)
		psPlot.trialPlotFig(self)

	def connectTeensy(self):
		baudRate=int(self.sesVarD['baudRate'])
		boardNum=int(self.sesVarD['comBoard'])
		self.teensy = serial.Serial('/dev/cu.usbmodem{}'.format(boardNum),baudRate)
		
	def runStimSession(self):
		
		psData.initSessionData(self)
		psData.initTrialData(self)
		psVariables.setPulseTrainVars(self,'ptVarD_chan0')
		psVariables.setPulseTrainVars(self,'ptVarD_chan1')

		pyStim.connectTeensy(self)
		self.sesVarD['totalTrials']=int(self.totalTrials_tv.get())
		self.sesVarD['currentSession']=int(self.currentSession_tv.get())
		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')
		self.lastTrial=int(self.sesVarD['tNum'])
		while (int(self.sesVarD['tNum'])-self.lastTrial)<int(self.sesVarD['totalTrials']):
			# pyStim.connectTeensy(self)
			print('start trial# {}'.format(int(self.sesVarD['tNum'])))
			self.initPulseTrain()			
			self.pulseTrainTrial()
			self.sesVarD['tNum']=int(self.sesVarD['tNum'])+1
			self.sesVarD['totalTrials']=int(self.totalTrials_tv.get())
		print('done')
		pyStim.saveSessionData(self)
		self.sesVarD['currentSession']=int(self.sesVarD['currentSession'])+1
		self.currentSession_tv.set('{}'.format(int(self.sesVarD['currentSession'])))
		psVariables.dictToPandas(self,self.sesVarD,'sesVarD')

		pyStim.cleanup(self)

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
				rf=pd.DataFrame({'psData.{}'.format(psData.trialStores[x]):tCo})
			elif x != 0:
				tf=pd.DataFrame({'psData.{}'.format(psData.trialStores[x]):tCo})
				rf=pd.concat([rf,tf],axis=1)

		try:
			tSavePath=self.trialDataPath + '/'
		except:
			tSavePath=self.dirPath_tv.get() + '/'

		#rf.to_csv('{}_trial_{}.csv'.format(self.sesVarD['animalID'],self.sesVarD['tNum']))

		rf.to_csv('{}{}_{}_s{}_trial_{}.csv'.\
			format(tSavePath,self.sesVarD['animalID'],self.dateSvStr, int(self.sesVarD['currentSession']),int(self.sesVarD['tNum'])))
		self.trialDataExists=0

	
	def updateSessionData(self):

		psData.trialNumber.append(int(self.sesVarD['tNum']))
		psData.trialTime.append(psData.tm[-1])
		psData.preTime.append(psData.tC[0])
		psData.stimType.append(self.s)
		psData.trialDuration.append(self.tDur)
		psData.stimAmp_ChanA.append((self.ptVarD_chan0['pulseAmpV']/3.3)*4095)
		psData.stimAmp_ChanB.append((self.ptVarD_chan1['pulseAmpV']/3.3)*4095)

	def saveSessionData(self):
		self.dateSvStr = datetime.datetime.fromtimestamp(time.time()).\
		strftime('%H%M_%m%d%Y')

		try:
			tSavePath=self.sesDataPath + '/'
		except:
			tSavePath=self.dirPath_tv.get() + '/'
			
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

		# rf.to_csv('{}_session_{}.csv'.\
		# 	format(self.sesVarD['animalID'],self.sesVarD['sessionNumber']))
		rf.to_csv('{}{}_{}_s{}_sessionData.csv'.\
			format(tSavePath,self.sesVarD['animalID'],self.dateSvStr, int(self.sesVarD['currentSession'])))
		self.sessionDataExists=0

		psUtil.exportAnimalMeta(self)


	def updatePlotCheck(self):

		if plt.fignum_exists(100):
			psPlot.updateTrialFig(self)
		self.cycleCount=0

	def initPulseTrain(self):
		
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

		self.tDur=int(int(self.sesVarD['tDur'])*int(self.sesVarD['sRate']))
		
		
		self.comObj=self.teensy
		

			
		self.current_milli_time = lambda: int(round(time.time() * 1000))
		self.initT=self.current_milli_time();
		
		self.resetVariables=0
		self.rxBit=0
		self.txBit=0

	def pulseTrainTrial(self):
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
					# # wait a bit (minimium of dt)
					# time.sleep(0.002)
					
					self.tR,self.rxBit=self.readSerialData(self.comObj,'vars',self.varCount)
					

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
					tDur=self.tDur
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
					self.tR,self.rxBit=self.readSerialData(self.comObj,'vars',self.varCount)
					

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
							self.comObj.write('{}{}>'.format(tHead,tVal).encode('utf-8'))
							self.txBit=1
							waitCount=0
							pyStim.updatePlotCheck(self)

						if len(varCheck)==0:
							self.varsSent=1
							doneOnce=0

					elif self.txBit==1:
						waitCount=waitCount+1
						self.tR,self.rxBit=self.readSerialData(self.comObj,'vars',self.varCount)
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
						if psData.pS[-1]==0:
							self.collecting=0
							
				
				while self.collecting==0:
					if initSt==0:
						psPlot.updateLastTrialFig(self)
						initSt=1
						pyStim.saveTrialData(self)
						pyStim.updateSessionData(self)
						

					self.teensy.write('a0>'.encode('utf-8'))
					self.inTrial ==0
					return()

root = Tk()
app = pyStim(root)
root.mainloop()
exit()