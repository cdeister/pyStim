from tkinter import *
import tkinter.filedialog as fd
import serial
import numpy as np
import matplotlib 
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import time
import datetime as DT
import random
import struct
import sys
import os
import pandas as pd
import scipy.stats as stats

comObj = serial.Serial('/dev/cu.usbmodem2828431',115200)

# **** edit these if you want
# for now, they can not be 0!
dwellTime=0.1
pulseTime=0.005
trainTime=15
nPulses=12
pAmp=1000

# Don't mess with this stuff
varCount=8
dataCount=6
sNum=6

#
sRate=5000
tDur=trainTime*sRate
iPInt=dwellTime*sRate
pDur=pulseTime*sRate

tm=[]
v1=[]
v2=[]
tC=[]


# send to state 0 to reset variables
resetVars=0
while resetVars==0:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==varCount and sR[0]=='vars':
		s=int(sR[sNum])
		if (s != 0):
			print('a')
			print(sR[sNum])
			comObj.write('s0>'.encode('utf-8'))
			time.sleep(0.005)
		elif s == 0:
			print('b')
			resetVars=1

print('reset')
trialSet=0


# send to state 1
while s != 1:
	comObj.write('s1>'.encode('utf-8'))
	time.sleep(0.005)
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==varCount and sR[0]=='vars':
		s=int(sR[sNum])
		aR=int(sR[1])
		pR=int(sR[2])
		tR=int(sR[3])
		nR=int(sR[4])
		ssR=int(sR[5])


if s==1:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==varCount and sR[0]=='vars':
		s=int(sR[sNum])
		aR=int(sR[1])
		pR=int(sR[2])
		tR=int(sR[3])
		nR=int(sR[4])
		ssR=int(sR[5])

		print('aa_{}_{}_{}_{}_{}_{}'.format(s,aR,pR,tR,nR,ssR))

	if aR==0:
		comObj.write('a{}>'.format(pAmp).encode('utf-8'))
		time.sleep(0.005)
	
	if pR==0:
		comObj.write('p{}>'.format(pDur).encode('utf-8'))
		time.sleep(0.005)

	if tR==0:
		comObj.write('t{}>'.format(tDur).encode('utf-8'))
		time.sleep(0.005)
	if nR==0:
		comObj.write('n{}>'.format(nPulses).encode('utf-8'))
		time.sleep(0.005)

	if ssR==0:
		comObj.write('r{}>'.format(iPInt).encode('utf-8'))
		time.sleep(0.005)

		



print('cc_{}'.format(s))

current_milli_time = lambda: int(round(time.time() * 10000))


				
while s!=2:
	comObj.flush()
	comObj.write('s2>'.encode('utf-8'))
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==varCount and sR[0]=='vars':
		s=int(sR[sNum])
		

n=1
bT=current_milli_time();
while n<=tDur:
	
	comObj.flush()
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==dataCount and sR[0]=='data' :
		tm.append(sR[3])
		v1.append(sR[1])
		v2.append(sR[2])
		tC.append(sR[4])
		n=n+1
		# print('r_{}_{}_{}'.format(s,n,sR[1]))

eT=current_milli_time();

while s==2:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==varCount and sR[0]=='vars':
		s=int(sR[sNum])
		comObj.write('s0>'.encode('utf-8'))


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
quit()