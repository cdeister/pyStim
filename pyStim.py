# pyStim v0.9
# _________________
# Works with microcontrollers that have hardward DACs, like the Teensy 3 line.
# It is intended to be used with a Teensy3.5/3.6, both of which have 2 analog outs.
#
# You need to load 'teensyStim.ino' onto your microcontroller.

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
		'animalID':"an1",'uiUpdateSamps':100,'sRate':1000,\
		'totalTrials':50,'sampsToPlot':500,'comBoard':2540591,\
		'baudRate':19200,'dacMaxVal':3.3,'dacMinVal':0,'adcBitDepth':8,\
		'dacBitDepth':12,'varCount':13,'sNum':1,'dataCount':8,\
		'serDelay':0.000001,'tNum':1,'tDur':3}
		exec('self.{}=sesVarD'.format(idString))
		# self.sesVarD['totalTrials']
		psVariables.dictToPandas(self,sesVarD,idString)


	def setPulseTrainVars(self,idString):

		ptVarD = {'dwellTime':50,'pulseTime':50,'nPulses':10,\
		'pulseAmpV':3.3,'baselineTime':1000}
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

class psPlot:

	def trialPlotFig(self):
		plt.style.use('dark_background')
		self.trialFramePosition='+370+0' # can be specified elsewhere
		self.updateTrialAxes=0
		
		self.trialFig = plt.figure(100,figsize=(4,5), dpi=100)
		tNum=self.sesVarD['tNum']
		self.trialFig.suptitle('trial # {} of {}'.format(tNum,self.sesVarD['totalTrials']),fontsize=10)
		self.trialFig.subplots_adjust(wspace=0.1,hspace=0.2)
		
		mng = plt.get_current_fig_manager()
		eval('mng.window.wm_geometry("{}")'.format(self.trialFramePosition))

		self.positionAxes=plt.subplot2grid([2,2],(0,0),colspan=2,rowspan=1)
		self.positionAxes.set_yticks([])
		self.positionAxes.set_xticks([])
		self.positionAxes.set_ylim([-100,4200])
		self.positionAxes.set_xlim([0,self.sesVarD['tDur']])
		self.positionAxes.set_title('current trial',fontsize=10)
		self.positionLine,=self.positionAxes.plot([1,1],color="olive",lw=1)
		self.positionLine2,=self.positionAxes.plot([1,1],color="cornflowerblue",lw=1)
		plt.show(block=False)

		self.lastTrialAxes=plt.subplot2grid([2,2],(1,0),colspan=2,rowspan=1)
		self.lastTrialAxes.set_yticks([])
		# self.lastTrialAxes.set_xticks([])
		self.lastTrialAxes.set_ylim([-500,4500])
		self.lastTrialAxes.set_xlim([0,self.sesVarD['tDur']])
		self.lastTrialAxes.set_title('last trial',fontsize=10)
		self.lastDataLine,=self.lastTrialAxes.plot([1,1],color="olive",lw=1)
		self.lastDataLine2,=self.lastTrialAxes.plot([1,1],color="cornflowerblue",lw=1)
		plt.show(block=False)

	
	def updateTrialFig(self):
		dT=np.divide(1,self.sesVarD['sRate'])
		splt=self.sesVarD['sampsToPlot']
		posPltYData=np.array(psData.v1[-int(splt):])
		posPltYData2=np.array(psData.v2[-int(splt):])
		x0=np.array(psData.tm[-int(splt):])
		x1=np.multiply(x0,dT)
		x0=[]
		tNum=self.sesVarD['tNum']
		self.trialFig.suptitle('trial # {} of {}'.format(tNum,self.sesVarD['totalTrials']),fontsize=10)
		
		if len(x1)>1:
			self.positionLine.set_xdata(x1)
			self.positionLine.set_ydata(posPltYData)
			self.positionLine2.set_xdata(x1)
			self.positionLine2.set_ydata(posPltYData2)
			self.positionAxes.draw_artist(self.positionLine)
			self.positionAxes.draw_artist(self.positionLine2)
			self.positionAxes.draw_artist(self.positionAxes.patch)

			self.trialFig.canvas.draw_idle()

		self.trialFig.canvas.flush_events()

	def updateLastTrialFig(self):
		
		dT=np.divide(1,self.sesVarD['sRate'])
		posPltYData=np.array(psData.v1)
		posPltYData2=np.array(psData.v2)

		x0=np.array(psData.tm)    
		x1=np.multiply(x0,dT)

		self.lastDataLine.set_xdata(x1)
		self.lastDataLine.set_ydata(posPltYData)
		self.lastDataLine2.set_xdata(x1)
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
		self.dirPath.set(self.dirPath_tv)
		self.setSesPath=1

	def mapAssign(self,l1,l2):
		for x in range(0,len(l1)):
			if type(l2[x])==int:
				exec('self.{}=int({})'.format(l1[x],l2[x])) 
			elif type(l2[x])==float:
				exec('self.{}=float({})'.format(l1[x],l2[x])) 

	def mapAssignStringEntries(self,l1,l2):
		for x in range(0,len(l1)):
			a=[l2[x]]
			exec('self.{}.set(a[0])'.format(l1[x]))

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

class psData:

	def initSessionData(self):
		psData.sessionStores='trialTime','preTime'
		for x in range(0,len(psData.sessionStores)):
			exec('{}=[]'.format(psData.sessionStores[x]))

	def initTrialData(self):
		psData.trialStores='tm','v1','v2','rv1','rv2','tC'
		psData.trialStoresIDs=[1,2,3,4,5,6]
		for x in range(0,len(psData.trialStores)): 
			exec('psData.{}=[]'.format(psData.trialStores[x]))


	def initTeensyStateData(self): # hacky

		psData.varHeader='b','c','d','e','f','g','h','i','j','k','l'	
		psData.varStates='bSt','cSt','dSt','eSt','fSt','gSt','hSt','iSt',\
		'jSt','kSt','lSt'
		psData.varNames='pAmpA','pDurA','iPIntA','nPulsesA','bDurA','tDur',\
		'pAmpB','pDurB','iPIntB','nPulsesB','bDurB'
		psData.varNums=[2,3,4,5,6,7,8,9,10,11,12]

	def saveTrialData(self):
		animalID=self.sesVarD['animalID']
		tNum=self.sesVarD['tNum']
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

class psWindow:

	def blankLine(self,targ,startRow):
		self.guiBuf=Label(targ, text="")
		self.guiBuf.grid(row=startRow,column=0,sticky=W)

	def mwQuitBtn(self):

		print('!!!! going down')
		print('... closed the com obj')
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

		self.animalID='yourID'
		self.dateStr = datetime.datetime.fromtimestamp(time.time()).\
		strftime('%H:%M (%m/%d/%Y)')

		# psWindow.blankLine(self.master,startRow)
		self.sessionStuffLabel = Label(self.master,text="Session Stuff: ",justify=LEFT).\
		grid(row=startRow+1, column=0,sticky=W)

		self.timeDisp = Label(self.master, text=' #{} started: '\
			.format(self.sesVarD['currentSession']) + self.dateStr,justify=LEFT)
		self.timeDisp.grid(row=startRow+2,column=0,sticky=W)

		self.dirPath_tv=StringVar(self.master)
		self.pathEntry=Entry(self.master,textvariable=self.dirPath_tv,width=24,bg='grey')
		self.pathEntry.grid(row=startRow+3,column=0,sticky=W)
		self.dirPath_tv.set(os.path.join(os.getcwd(),self.animalID))

		self.setPath_button = Button(self.master,text="<- Set Path",\
			command=lambda:psWindow.mwPathBtn(self),width=self.col2BW)
		self.setPath_button.grid(row=startRow+3,column=2)

		self.aIDLabel=Label(self.master, text="animal id:")\
		.grid(row=startRow+4,column=0,sticky=W)
		self.animalIDStr_tv=StringVar(self.master)
		self.animalIDEntry=Entry(self.master,textvariable=\
			self.animalIDStr_tv,width=14,bg='grey')
		self.animalIDEntry.grid(row=startRow+4,column=0,sticky=E)
		self.animalIDStr_tv.set(self.animalID)

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
		self.currentSession_tv.set(self.sesVarD['currentSession'])
		self.curSession_entry=Entry(self.master,textvariable=\
			self.currentSession_tv,width=10)
		self.curSession_entry.grid(row=startRow+6,column=0,sticky=E)



		self.loadAnimalMetaBtn = Button(self.master,text = 'Load Metadata',\
			width = self.col2BW,command = lambda: psWindow.mwLoadMetaBtn(self))
		self.loadAnimalMetaBtn.grid(row=startRow+1, column=2)
		self.loadAnimalMetaBtn.config(state=NORMAL)

		self.saveCurrentMetaBtn=Button(self.master,text="Save Cur. Meta",\
			command=lambda:pdUtil.exportAnimalMeta(self), width=self.col2BW)
		self.saveCurrentMetaBtn.grid(row=startRow+2,column=2)

class psTypes:

	def yup(self):
		print('who')

class pyStim:

	def __init__(self,master):

		psData.initSessionData(self)
		psVariables.setSessionVars(self,'sesVarD')

		
		self.master = master
		self.frame = Frame(self.master)
		root.wm_geometry("+0+0")
		psWindow.psWindowPopulate(self)
		psPlot.trialPlotFig(self)

	def connectTeensy(self):
		baudRate=self.sesVarD['baudRate']
		boardNum=self.sesVarD['comBoard']
		self.teensy = serial.Serial('/dev/cu.usbmodem{}'.format(boardNum),baudRate)
		
	def runStimSession(self):
		
		psData.initSessionData(self)
		psData.initTrialData(self)
		psVariables.setSessionVars(self,'sesVarD')
		psVariables.setPulseTrainVars(self,'ptVarD_chan0')
		psVariables.setPulseTrainVars(self,'ptVarD_chan1')

		
		sA=[0,0.5,1.0,1.5,2.0,3.3]
		sB=[0,0.5,1.0,1.5,2.0,3.3]
		
		print(max(sA))
		self.preTimes=[]
		while self.sesVarD['tNum']<=self.sesVarD['totalTrials']:
			
			c1=np.random.random_integers(len(sA))
			c2=np.random.random_integers(len(sB))
			print(c1)

			self.ptVarD_chan0['pulseAmpV']=sA[c2-1]
			self.ptVarD_chan1['pulseAmpV']=sA[c1-1]
			pyStim.connectTeensy(self) 
			
			print('trial={}'.format(self.sesVarD['tNum']))
			self.initPulseTrain()			
			self.pulseTrainTrial()
			psPlot.updateLastTrialFig(self)
			self.sesVarD['tNum']=self.sesVarD['tNum']+1
			self.teensy.close()
		pyStim.exportAnimalMeta(self)
		print(self.preTimes)
		print('done')
		return()
		
		
	def cleanup(self):
		while self.s != 0:
			self.tR,self.tU=self.readSerialData(self.comObj,'vars',self.varCount)
			if self.tU:
				self.s=int(self.tR[self.sNum])
			self.teensy.write('a0>'.encode('utf-8'))
			self.teensy.flush()

		self.teensy.close()
		#self.teensy.delete()

	def readSerialData(self,comObj,headerString,headerCount):

		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==headerCount and sR[0]==headerString:
			newData=1
		else:
			newData=0
		return sR,newData

	def exportAnimalMeta(self):

		self.sesVarD_Bindings.to_csv('sesVars.csv')
		self.ptVarD_chan0_Bindings.to_csv('ptAVar.csv')
		self.ptVarD_chan1_Bindings.to_csv('ptBVar.csv')

	def updatePlotCheck(self):

		if plt.fignum_exists(100):
			psPlot.updateTrialFig(self)
		self.cycleCount=0

	def initPulseTrain(self):
		
		self.inTrial=1
		self.s=-1
		psData.initTeensyStateData(self)
		psData.initTrialData(self)
		self.sNum=self.sesVarD['sNum']
		self.varStates=psData.varStates
		self.varNums=psData.varNums
		self.varNames=psData.varNames
		self.varHeader=psData.varHeader
		self.varCount=self.sesVarD['varCount']
		self.dataCount=self.sesVarD['dataCount']
		self.serDelay=self.sesVarD['serDelay']
		self.tDur=int(self.sesVarD['tDur']*self.sesVarD['sRate'])
		
		
		self.tNum=self.sesVarD['tNum']
		self.comObj=self.teensy
		self.animalID=self.sesVarD['animalID']

			
		self.current_milli_time = lambda: int(round(time.time() * 1000))
		self.curVarState = lambda x: x==0 

			
		while self.s != 0:
			self.tR,self.tU=self.readSerialData(self.comObj,'vars',self.varCount)
			if self.tU:
				self.s=int(self.tR[self.sNum])
			self.teensy.write('a0>'.encode('utf-8'))
			self.teensy.flush()

		print('syncd')
		self.initT=self.current_milli_time();
		self.resetVariables=0

	def pulseTrainTrial(self):
		while self.inTrial ==1:
			if self.s==0:				
				if self.resetVariables==0:
					self.tR,self.tU=self.readSerialData(self.comObj,'vars',self.varCount)
					if self.tU:
						self.s=int(self.tR[self.sNum])
					n=1
					tDur=self.tDur
					pAmpA=(self.ptVarD_chan0['pulseAmpV']/3.3)*4095
					pDurA=self.ptVarD_chan0['pulseTime']
					iPIntA=self.ptVarD_chan0['dwellTime']
					nPulsesA=self.ptVarD_chan0['nPulses']
					bDurA=self.ptVarD_chan0['baselineTime']

					pAmpB=(self.ptVarD_chan1['pulseAmpV']/3.3)*4095
					pDurB=self.ptVarD_chan1['pulseTime']
					iPIntB=self.ptVarD_chan1['dwellTime']
					nPulsesB=self.ptVarD_chan1['nPulses']
					bDurB=self.ptVarD_chan1['baselineTime']
					pST=self.current_milli_time()
					self.varsSent=0
					self.resetVariables=1
					varCheck=np.zeros(len(self.varStates))
					s1Counter=0

				elif self.resetVariables==1:
					self.tR,self.tU=self.readSerialData(self.comObj,'vars',self.varCount)
					if self.tU:
						self.s=int(self.tR[self.sNum])						
						self.teensy.write('a1>'.encode('utf-8'))
						self.teensy.flush()
						

			
			elif self.s == 1:
				self.tR,self.tU=self.readSerialData(self.comObj,'vars',self.varCount)
				if self.tU:
					
					s1Counter=s1Counter+1
					self.s=int(self.tR[self.sNum])
					
					if self.varsSent==0:
						varsNotSet=np.hstack(np.argwhere(varCheck==0))
					for x in range(0,len(varsNotSet)):
						lX=varsNotSet[x]
						exec('{}=self.tR[{}]'.format(self.varStates[lX],self.varNums[lX]))
						a=int(self.tR[self.varNums[lX]])
						varCheck[lX]=int(a)
						
						if np.sum(varCheck)==len(self.varStates):
							self.varsSent=1							

						if a==0:
							tVal=str(int(eval('{}'.format(psData.varNames[lX]))))
							self.comObj.write('{}{}>'.format(self.varHeader[lX],tVal).encode('utf-8'))
							if s1Counter>self.sesVarD['uiUpdateSamps']:
								pyStim.updatePlotCheck(self)
								s1Counter=0
							self.teensy.flush()

				if self.varsSent==1:
					bT=self.current_milli_time();
					self.comObj.write('a2>'.encode('utf-8'))
							
			elif self.s==2:
				while n<=self.tDur:
					dR,dU=self.readSerialData(self.teensy,'data',self.dataCount)
					if dU:
						if n % self.sesVarD['uiUpdateSamps'] == 0:
							pyStim.updatePlotCheck(self)
						for x in range(0,len(psData.trialStores)):
							a=dR[psData.trialStoresIDs[x]]
							exec('psData.{}.append({})'.format(psData.trialStores[x],a))
						n=n+1
						if n % self.sesVarD['uiUpdateSamps'] == 0:
							pyStim.updatePlotCheck(self)

					if n==self.tDur:						
						print('fts={}'.format(psData.tC[-1]-psData.tC[0]))
						print(bT-self.initT)
						self.preTimes.append(bT-self.initT)
						print('time={}'.format(psData.tm[-1]-psData.tm[0]))
						print('fts={}'.format(psData.tm[-1]))
						self.inTrial==0
						return()
				

root = Tk()
app = pyStim(root)
root.mainloop()
exit()