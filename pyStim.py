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

comObj = serial.Serial('/dev/cu.usbmodem2828431',115200)

# **** edit these if you want

# session
sRate=2000  # samples/sec

# pulse train A
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

trainTime=5
totalTrials=1

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
tNum=1


current_milli_time = lambda: int(round(time.time() * 1000))

while tNum<=totalTrials:
	tm=[]
	v1=[]
	v2=[]
	rv1=[]
	rv2=[]
	tC=[]
	pST=current_milli_time();

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
			bSt=int(sR[2])
			cSt=int(sR[3])
			dSt=int(sR[4])
			eSt=int(sR[5])
			fSt=int(sR[6])
			gSt=int(sR[7])
			hSt=int(sR[8])
			iSt=int(sR[9])
			jSt=int(sR[10])
			kSt=int(sR[11])
			lSt=int(sR[12])
			


	if s==1:
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==varCount and sR[0]=='vars':
			s=int(sR[sNum])

			bSt=int(sR[2])
			cSt=int(sR[3])
			dSt=int(sR[4])
			eSt=int(sR[5])
			fSt=int(sR[6])
			gSt=int(sR[7])
			hSt=int(sR[8])
			iSt=int(sR[9])
			jSt=int(sR[10])
			kSt=int(sR[11])
			lSt=int(sR[12])
			


		if bSt==0:
			comObj.write('b{}>'.format(pAmpA).encode('utf-8'))
			time.sleep(0.025)
		
		if cSt==0:
			comObj.write('c{}>'.format(pDurA).encode('utf-8'))
			time.sleep(0.025)
		if dSt==0:
			comObj.write('d{}>'.format(iPIntA).encode('utf-8'))
			time.sleep(0.025)
		if eSt==0:
			comObj.write('e{}>'.format(nPulsesA).encode('utf-8'))
			time.sleep(0.025)
		if fSt==0:
			comObj.write('f{}>'.format(bDurA).encode('utf-8'))
			time.sleep(0.025)
		if gSt==0:
			comObj.write('g{}>'.format(tDur).encode('utf-8'))
			time.sleep(0.025)
		if hSt==0:
			comObj.write('h{}>'.format(pAmpB).encode('utf-8'))
			time.sleep(0.025)
		if iSt==0:
			comObj.write('i{}>'.format(pDurB).encode('utf-8'))
			time.sleep(0.025)
		if jSt==0:
			comObj.write('j{}>'.format(iPIntB).encode('utf-8'))
			time.sleep(0.025)
		if kSt==0:
			comObj.write('k{}>'.format(nPulsesB).encode('utf-8'))
			time.sleep(0.025)
		if lSt==0:
			comObj.write('l{}>'.format(bDurB).encode('utf-8'))
			time.sleep(0.025)

			
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
			print('v1/v2: {}_{}'.format(sR[6],sR[7]))

	eT=current_milli_time();

	while s==2:	
		sR=comObj.readline().strip().decode()
		sR=sR.split(',')
		if len(sR)==varCount and sR[0]=='vars':
			s=int(sR[sNum])
			comObj.write('a0>'.encode('utf-8'))


	print('eT: {}'.format(eT-bT))
	
	tCo=[]
	saveStreams='tm','v1','v2','rv1','rv2','tC'
	for x in range(0,len(saveStreams)):
		exec('tCo={}'.format(saveStreams[x]))
		if x==0:
			rf=pd.DataFrame({'{}'.format(saveStreams[x]):tCo})
		elif x != 0:
			tf=pd.DataFrame({'{}'.format(saveStreams[x]):tCo})
			rf=pd.concat([rf,tf],axis=1)

	rf.to_csv('test_{}.csv'.format(tNum))
	trialTime.append(eT-bT)
	print('trial_{} done; pre took {}'.format(tNum,bT-pST))
	tNum=tNum+1

# end the session
tCo=[]
saveStreams=[]
saveStreams=['trialTime']
for x in range(0,len(saveStreams)):
	exec('tCo={}'.format(saveStreams[x]))
	if x==0:
		rf=pd.DataFrame({'{}'.format(saveStreams[x]):tCo})
	elif x != 0:
		tf=pd.DataFrame({'{}'.format(saveStreams[x]):tCo})
		rf=pd.concat([rf,tf],axis=1)
rf.to_csv('session_{}.csv'.format(1))

# clean up
comObj.close()
print('done')
sys.exit(0)