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
		'lickThresholdStrValB':550,'totalTrials':150,\
		'sampsToPlot':1000,'comPath':"/dev/cu.usbmodem2762721",\
		'baudRate':19200,'dacMaxVal':3.3,'dacMinVal':0,'adcBitDepth':8,\
		'dacBitDepth':12,'varCount':13,'sNum':1,'dataCount':8,\
		'serDelay':0.005,'tNum':1,'tDur':5}
		exec('self.{}=sesVarD'.format(idString))

		psVariables.dictToPandas(self,sesVarD,idString)

	def setPulseTrainVars(self,idString):

		ptVarD = {'dwellTime':0.100,'pulseTime':0.100,'nPulses':10,\
		'pulseAmpV':3.3,'baselineTime':3}
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
		psData.sessionStores='trialTime','preTime'
		for x in range(0,len(psData.sessionStores)):
			exec('{}=[]'.format(psData.sessionStores[x]))

	def initTrialData(self):
		psData.trialStores='tm','v1','v2','rv1','rv2','tC'
		psData.trialStoresIDs=[1,2,3,4,5,6]
		for x in range(0,len(psData.trialStores)): 
			exec('psData.{}=[]'.format(psData.trialStores[x]))

	def initTeensyStateData(self): # hacky
		print('debug: init')

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

class pyStim:

	def __init__(self,master):
		baudRate=19200
		boardNum=2540591

		self.teensy = serial.Serial('/dev/cu.usbmodem{}'.format(boardNum),baudRate)
		self.master = master
		self.frame = Frame(self.master)
		root.wm_geometry("+0+0")
		psData.initSessionData(self)
		psVariables.setSessionVars(self,'sesVarD')
		
		self.pulseTrainTrial()
		pyStim.exportAnimalMeta(self)
		self.teensy.close()
		print('done')


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

	def pulseTrainTrial(self):
		psVariables.setPulseTrainVars(self,'ptVarD_chan0')
		psVariables.setPulseTrainVars(self,'ptVarD_chan1')
		psData.initTeensyStateData(self)
		psData.initTrialData(self)

		# ugly hack
		pAmpA=self.ptVarD_chan0['pulseAmpV']
		pDurA=self.ptVarD_chan0['pulseTime']
		iPIntA=self.ptVarD_chan0['dwellTime']
		nPulsesA=self.ptVarD_chan0['nPulses']
		bDurA=self.ptVarD_chan0['baselineTime']
		pAmpB=self.ptVarD_chan1['pulseAmpV']
		pDurB=self.ptVarD_chan1['pulseTime']
		iPIntB=self.ptVarD_chan1['dwellTime']
		nPulsesB=self.ptVarD_chan1['nPulses']
		bDurB=self.ptVarD_chan1['baselineTime']
		tDur=self.sesVarD['tDur']

		# local vars
		sNum=self.sesVarD['sNum']
		varStates=psData.varStates
		varNums=psData.varNums
		varNames=psData.varNames
		varHeader=psData.varHeader
		varCount=self.sesVarD['varCount']
		dataCount=self.sesVarD['dataCount']
		serDelay=self.sesVarD['serDelay']
		tDur=self.sesVarD['tDur']
		tNum=self.sesVarD['tNum']
		resetVars=0
		comObj=self.teensy
		animalID=self.sesVarD['animalID']


		current_milli_time = lambda: int(round(time.time() * 1000))
		curVarState = lambda x: x==0 

		# send to state 0 to reset variables
		while resetVars==0:
			tR,tU=self.readSerialData(comObj,'vars',varCount)
			if tU:
				s=int(tR[sNum])
				if (s != 0):
					self.teensy.write('a0>'.encode('utf-8'))
					time.sleep(0.005)
				elif s == 0:
					resetVars=1

		# send to state 1
		while s != 1:
			comObj.write('a1>'.encode('utf-8'))
			time.sleep(0.025)
			tR,tU=self.readSerialData(comObj,'vars',varCount)
			print(tR)
			if tU:
				s=int(tR[sNum])
				for x in range(0,len(varStates)):
					exec('{}=tR[{}]'.format(varStates[x],varNums[x]))

		if s==1:
			tR,tU=self.readSerialData(comObj,'vars',varCount)
			if tU:
				s=int(tR[sNum])
				for x in range(0,len(varStates)):
					exec('{}=tR[{}]'.format(varStates[x],varNums[x]))
		
			for x in range(0,len(varStates)):
				a=eval('curVarState({})'.format(varStates[x]))
				if a==0:
					tVal=eval(varNames[x])
					comObj.write('{}{}>'.format(varHeader[x],tVal).encode('utf-8'))
					time.sleep(serDelay)
				print(a)
		print(tDur)
		print('queued_{}'.format(tNum))
		bT=current_milli_time();

		while s!=2:
			comObj.flush()
			comObj.write('a2>'.encode('utf-8'))
			tR,tU=self.readSerialData(comObj,'vars',varCount)
			if tU:
				s=int(tR[sNum])

		n=1
		while n<=tDur:
			tR,tU=self.readSerialData(comObj,'data',dataCount)
			if tU:
				for x in range(0,len(psData.trialStores)):
					exec('{}.append(tR[{}])'.format(psData.trialStores[x],psData.trialStoresIDs[x]))
				n=n+1

		eT=current_milli_time();

		while s!=2:
			comObj.flush()
			comObj.write('a2>'.encode('utf-8'))
			tR,tU=self.readSerialData(comObj,'vars',varCount)
			if tU:
				s=int(tR[sNum])
				comObj.write('a0>'.encode('utf-8'))

		self.teTime=eT-bT
		self.tpTime=bT-pST
		print('eT: {}'.format(self.teTime))
		print('pT: {}'.format(self.tpTime))
		print('{}_trial_{} done; pre took {}'.format(animalID,tNum,self.tpTime))
		psData.saveTrialData(self)
		self.sesVarD['tNum']=tNum+1



root = Tk()
app = pyStim(root)
root.mainloop()
exit()