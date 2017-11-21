# pyStim v0.75
# _________________
# Works with microcontrollers that have hardward DACs, like the Teensy 3 line.
# It is intended to be used with a Teensy3.5/3.6, both of which have 2 analog outs.
# All configuration is script based at this point. See the edit block below for variables.
# GUI Coming. The GUI will unlock other capabilities.
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
import sys
import os
import pandas as pd

comObj = serial.Serial('/dev/cu.usbmodem2405571',115200)

#******************************
# **** edit these if you want
#******************************


# session
sRate=1000  # samples/sec (this is set by the teensy, we just need to know it)

# pulse train A
animalID='testMouse'

dwellTimeA=0.100  # in S
pulseTimeA=0.100  # in S
nPulsesA=10  	  
pulseAmpV_A=10   # in V (0-3.3V)
baselineTimeA=0.5 # in S

# pulse train B
dwellTimeB=0.100 # in S
pulseTimeB=0.100 # in S
nPulsesB=10
pulseAmpV_B=10  # in V (0-3.3V)
baselineTimeB=2 # in S

trainTime=5 # in S
totalTrials=10

# Don't mess with this stuff
# describes the "vars" report from teensy
varCount=13
sNum=1
# describes the "data" report from teensy
dataCount=8


# Scale things (mostly convert time to samples)

if pulseAmpV_A<0:
	abs(pulseAmpV_A)
if pulseAmpV_B<0:
	abs(pulseAmpV_B)
if pulseAmpV_A>3.3:
	pulseAmpV_A=3.3
if pulseAmpV_B>3.3:
	pulseAmpV_B=3.3

tDur=trainTime*sRate

bDurA=baselineTimeA*sRate
iPIntA=dwellTimeA*sRate
pDurA=pulseTimeA*sRate
pAmpA=int((pulseAmpV_A/3.3)*4095)


bDurB=baselineTimeB*sRate
iPIntB=dwellTimeB*sRate
pDurB=pulseTimeB*sRate
pAmpB=int((pulseAmpV_B/3.3)*4095)

print(pAmpA)
print(pAmpB)


trialTime=[]
preTime=[]


tNum=1

sessionStores='trialTime','preTime'
for x in range(0,len(sessionStores)):
		exec('{}=[]'.format(sessionStores[x]))


current_milli_time = lambda: int(round(time.time() * 1000))

while tNum<=totalTrials:
	trialStores='tm','v1','v2','rv1','rv2','tC'
	trialStoresIDs=[1,2,3,4,5,6]
	for x in range(0,len(trialStores)): 
		exec('{}=[]'.format(trialStores[x]))



	
	pST=current_milli_time();
	
	

	varHeader='b','c','d','e','f','g','h','i','j','k','l'	
	varStates='bSt','cSt','dSt','eSt','fSt','gSt','hSt','iSt','jSt','kSt','lSt'
	varNames='pAmpA','pDurA','iPIntA','nPulsesA','bDurA','tDur','pAmpB','pDurB','iPIntB','nPulsesB','bDurB'
	varNums=[2,3,4,5,6,7,8,9,10,11,12]

	# send to state 0 to reset variables
	resetVars=0
	while resetVars==0:
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==varCount and sR[0]=='vars':
			s=int(sR[sNum])
			if (s != 0):
				comObj.write('a0>'.encode('utf-8'))
				time.sleep(0.005)
			elif s == 0:
				
				resetVars=1

	# send to state 1
	while s != 1:
		comObj.write('a1>'.encode('utf-8'))
		time.sleep(0.025)
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==varCount and sR[0]=='vars':

			s=int(sR[sNum])
			for x in range(0,len(varStates)):
				exec('{}=sR[{}]'.format(varStates[x],varNums[x]))

			


	if s==1:
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==varCount and sR[0]=='vars':
			s=int(sR[sNum])

			for x in range(0,len(varStates)):
				exec('{}=sR[{}]'.format(varStates[x],varNums[x]))
		
		
		serDelay=0.025
		curVarState = lambda x: x==0 
		for x in range(0,len(varStates)):
			a=eval('curVarState({})'.format(varStates[x]))
			if a==0:
				tVal=eval(varNames[x])
				comObj.write('{}{}>'.format(varHeader[x],tVal).encode('utf-8'))
				time.sleep(serDelay)
				print('{}{}>'.format(varHeader[x],varNames[x]))
			
	print('queued_{}'.format(tNum))
	bT=current_milli_time();

	while s!=2:
		comObj.flush()
		comObj.write('a2>'.encode('utf-8'))
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==varCount and sR[0]=='vars':
			s=int(sR[sNum])
			

	n=1
	while n<=tDur:
		
		# comObj.flush()
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==dataCount and sR[0]=='data' :
			tm.append(sR[1])
			v1.append(sR[2])
			v2.append(sR[3])
			rv1.append(sR[4])
			rv2.append(sR[5])
			tC.append(sR[6])
			n=n+1

	eT=current_milli_time();

	while s==2:	
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==varCount and sR[0]=='vars':
			s=int(sR[sNum])
			comObj.write('a0>'.encode('utf-8'))


	print('eT: {}'.format(eT-bT))
	
	tCo=[]
	trialStores='tm','v1','v2','rv1','rv2','tC'
	for x in range(0,len(trialStores)):
		exec('tCo={}'.format(trialStores[x]))
		if x==0:
			rf=pd.DataFrame({'{}'.format(trialStores[x]):tCo})
		elif x != 0:
			tf=pd.DataFrame({'{}'.format(trialStores[x]):tCo})
			rf=pd.concat([rf,tf],axis=1)

	rf.to_csv('test_{}.csv'.format(tNum))
	trialTime.append(eT-bT)
	print('{}_trial_{} done; pre took {}'.format(animalID,tNum,bT-pST))
	tNum=tNum+1

# end the session
tCo=[]

for x in range(0,len(sessionStores)):
	exec('tCo={}'.format(sessionStores[x]))
	if x==0:
		rf=pd.DataFrame({'{}'.format(sessionStores[x]):tCo})
	elif x != 0:
		tf=pd.DataFrame({'{}'.format(sessionStores[x]):tCo})
		rf=pd.concat([rf,tf],axis=1)
rf.to_csv('{}_session_{}.csv'.format(animalID,1))

# clean up
comObj.close()
print('done')
sys.exit(0)