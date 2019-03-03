#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Open debug file and write whatever in it.
#Pass[0]: debug data to write

def write_debug(data) :
	
	data = str.splitlines(data)
	b = ''
	for i in data :
		a = str(datetime.datetime.now()) + ': ' + i + '\n'
		b = b + a

	try :
		debug = open(ddir, 'a')
		debug.write(b)
		debug.close()
	except :
		print('Was not able to write to ' + ddir + '!\n')
	
	return()


# In[2]:


#QueWay responder for offline testing

import os
import time
import datetime
from shutil import copy
from random import randint

ddir = os.getcwd() + '/offline_debug.txt'
write_debug('hello world')

os.system("python ./MiscFunc.py")
from MiscFunc import *

qwdir = clean_win_path(os.getcwd() + '/Offline/')
rask = qwdir + 'REMOTE.ASK'
rans = qwdir + 'REMOTE.ANS'
rmsg = qwdir + 'REMOTE.MSG'
outdir = qwdir + 'OUT/'

a = test_dir(outdir,True)
if not a :
	msg = 'Was not able to find or make ' + outdir + '! Program will close!'
	print(msg)
	write_debug(msg + '\n')
	time.sleep(5)
	exit()

pics = ['offline.jpg','grid.jpg']

for i in pics :
	imgloc = clean_win_path(qwdir + i)
	b = test_dir(imgloc)
	c = clean_win_path(os.getcwd() + '\\' + i)
	
	if not b :
		try :
			copy(c,imgloc)
		except :
			write_debug('Copying offline image \"' + imgloc + '\" failed!\n')
			test_dir(c)
		else :
			write_debug('Copied offline image to \"' + imgloc + '\"\n')

imgloc = qwdir + 'offline.jpg'

inivars = ['getdir','retrycnt','spcname']
inidir = os.getcwd() + '/QueWay.ini'

a = test_dir(inidir)
if not a :
	msg = 'Was not able to find ' + inidir + '! Program will close!'
	print(msg)
	write_debug(msg + '\n')
	time.sleep(5)
	exit()

a,b,c = load_settings(inidir,inivars)

if a == {} :
	msg = 'Did not load variables from ' + inidir + '! Program will close!'
	print(msg)
	write_debug(msg + '\n')
	time.sleep(5)
	exit()
	
for i in a :
	globals()[i] = a[i]

os.system("python ./RMFunc.py")
from RMFunc import *


# In[3]:


#'','HELP','GET_DIR_LIST','CHANGE_PART_DIR','GET_PART_LIST3','EXECUTE_PATH_PART_PROGRAM','GENMSG'
status = ''

def do_comm(stat) :
	
	if stat == '' :
		ask = read_file(rask,True)
		if len(ask) != 0 :
			stat = str(ask[0])
	
	elif stat == 'HELP' :
		msg = ['OFFLINE','HELP','REPLY']
		write_file(msg,rans)
		stat = ''
		
	elif stat == 'GET_DIR_LIST' :
		msg = ['1',getdir,'OK']
		write_file(msg,rans)
		stat = ''

	elif stat == 'CHANGE_PART_DIR' :
		msg = ['OK']
		write_file(msg,rans)
		stat = ''
		
	elif stat == 'GET_PART_LIST3' :
		a = qwdir + getdir
		a = do_win_path(a)
		b = '2'
		c = '491100.A7 PREM RV2.0\t' + imgloc
		c = do_win_path(c)
		d = '* 491100.A7 PREM RV1.0'
		e = '* 491100.A7 PREM RV2.0'
		cc = '491100.A7 SINT RV1.0\t' + imgloc
		cc = do_win_path(cc)
		dd = '* 491100.A7 SINT RV1.0'
		f = 'OK'
		msg = [a,b,c,d,e,cc,dd,f]
		write_file(msg,rans)
		stat = ''
		
	elif stat == 'CHANGE_PART_DIR' :
		msg = ['OK']
		write_file(msg,rans)
		stat = ''
		
	elif stat == 'EXECUTE_PATH_PART_PROGRAM' :
		msg = ['OK']
		write_file(msg,rans)
		genmsg()
		stat = ''    
		
	else :
		stat = ''
		
	return(stat)
	

def wait_loop(a) :
	a = do_comm(a) 
	time.sleep(0.2)
	write_debug('status is: ' + a + '.\n')
	wait_loop(a)
	
	return()
	
def genmsg() :
	a = randint(30,60)
	print('sleep time: ' + str(a))
	time.sleep(a)
	a = randint(1,100)
	if a < 10 :
		msg = ['PPERR']
	elif a > 95 :
		msg = ['TEST']
	else :
		msg = ['PPEND']
	print('result: ' + msg[0])
	write_file(msg,rmsg)
	
	return()


# In[ ]:


wait_loop(status)
