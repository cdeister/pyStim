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
# for now, they can not be 0!

dwellTimeA=0.195
pulseTimeA=0.005 
nPulsesA=10  
pulseAmpV_A=1   # in V (0-3.3V)
baselineTimeA=2.2

dwellTimeB=0.195
pulseTimeB=0.005
nPulsesB=40
pulseAmpV_B=1 
baselineTimeB=2

trainTime=5

# Don't mess with this stuff
# describes the "vars" report from teensy
varCount=13
sNum=1
# describes the "data" report from teensy
dataCount=6


# 
sRate=2000
tDur=trainTime*sRate

bDurA=baselineTimeA*sRate
iPIntA=dwellTimeA*sRate
pDurA=pulseTimeA*sRate
pAmpA=int((pulseAmpV_A/3.3)*4095)


bDurB=baselineTimeB*sRate
iPIntB=dwellTimeB*sRate
pDurB=pulseTimeB*sRate
pAmpB=int((pulseAmpV_B/3.3)*4095)



tm=[]
v1=[]
v2=[]
tC=[]

current_milli_time = lambda: int(round(time.time() * 1000))

# send to state 0 to reset variables
resetVars=0
print('d1')
while resetVars==0:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==varCount and sR[0]=='vars':
		s=int(sR[sNum])
		if (s != 0):
			print('a')
			comObj.write('a0>'.encode('utf-8'))
			time.sleep(0.005)
		elif s == 0:
			print('b')
			resetVars=1

print('d2')
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

		
print('cc_{}'.format(s))
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
		v1.append(sR[3])
		v2.append(sR[4])
		tC.append(sR[2])
		n=n+1

eT=current_milli_time();

while s==2:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==varCount and sR[0]=='vars':
		s=int(sR[sNum])
		comObj.write('a0>'.encode('utf-8'))


print('eT: {}'.format(eT-bT))
print('end_{}'.format(s))
tCo=[]
saveStreams='tm','v1','v2','tC'
for x in range(0,len(saveStreams)):
	exec('tCo={}'.format(saveStreams[x]))
	if x==0:
		rf=pd.DataFrame({'{}'.format(saveStreams[x]):tCo})
	elif x != 0:
		tf=pd.DataFrame({'{}'.format(saveStreams[x]):tCo})
		rf=pd.concat([rf,tf],axis=1)

rf.to_csv('test.csv')
comObj.close()
print('done')
sys.exit(0)