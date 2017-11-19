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

comObj = serial.Serial('/dev/cu.usbmodem2828431',115200)

n=1
tm=[]
v1=[]
v2=[]
tC=[]


resetVars=0
while resetVars==0:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==4 and sR[0]=='vars':
		s=int(sR[3])
		if (s != 0):
			print('a')
			print(sR[3])
			comObj.write('s0>'.encode('utf-8'))
		elif s == 0:
			print('b')
			resetVars=1

print('reset')
comObj.flush()
trialSet=0

if s == 3:
	trialSet=1

while trialSet==0:
	comObj.write('s1>'.encode('utf-8'))
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==4 and sR[0]=='vars':
		s=int(sR[3])

		if s != 1:
			comObj.write('s1>'.encode('utf-8'))
		elif s == 1:
			if int(sR[1])==0:
				print('aa')
				comObj.write('a978>'.encode('utf-8'))
			if int(sR[2])==0:
				print('bb')
				comObj.write('p200>'.encode('utf-8'))
			if int(sR[1])==1 and int(sR[2])==1 and int(sR[3])==1:
				print('cc')
				trialSet=1
			elif s == 3:
				print('dd')
				trialSet=1
				
while s!=2:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==4 and sR[0]=='vars':
		s=int(sR[3])
		comObj.flush()
		comObj.write('s2>'.encode('utf-8'))




while n<=100000:
	comObj.flush()
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==5 and sR[0]=='data' :
		tm.append(sR[3])
		v1.append(sR[1])
		v2.append(sR[2])
		tC.append(sR[4])
		n=n+1

				
while s==2:
	sR=comObj.readline().strip().decode()
	sR=sR.split(',')
	if len(sR)==4 and sR[0]=='vars':
		s=int(sR[3])
		comObj.flush()
		comObj.write('s0>'.encode('utf-8'))


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