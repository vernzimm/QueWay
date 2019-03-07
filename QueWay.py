#!/usr/bin/env python
# coding: utf-8


#Open debug file and write whatever in it, also write to the console.
#Pass[0]: debug data to write
#Set[0]: put debug into rootque for console.

def write_debug(data) :
	
	data = str.splitlines(data)
	b = ''
	for i in data :
		a = str(datetime.datetime.now()) + ': ' + i + '\n'
		b = b + a
		c = i + '\n'
		rootque.put(c)

	if writedbg :
		try :
			debug = open(ddir, 'a')
			debug.write(b)
			debug.close()
		except :
			d = 'Exception trying to write to ' + ddir + '!\n'
			rootque.put(d)
	
	return()

#Run as a separate thread and try getting from rootque and putting in console.
#Set[0]: insert last line (if any) from rootque in econsole.

def rootque_loop():
	
	a = 'set'
	while a != '' :
		try :
			a = rootque.get(block = False)
			econsole.insert(tk.END,a)
			econsole.see(tk.END)
		except :
			a = ''
			
		if current_thread() is main_thread():
			root.update()
			
		time.sleep(0.05)



import os
import time
import datetime
import csv
import tkinter as tk
from tkinter import ttk
from PIL import Image as imgget
from PIL import ImageTk
from concurrent.futures import ThreadPoolExecutor as TPEx
from threading import current_thread, main_thread
import queue
import subprocess as sub
import sys
from shutil import copy
import logging as log

writedbg = True
runloop = True
mainloop = False
rootque = queue.Queue()

ddir = os.getcwd() + '/debug.txt'
write_debug('hello world')

root = tk.Tk()
root.title('QueWay')
root.resizable(False, False)

econsole = tk.Text(root, width = 120, height = 8, exportselection = False, wrap = tk.WORD)
econsole.grid(column = 0, row = 2, columnspan = 3, sticky = (tk.N, tk.S, tk.W, tk.E))  

rootque_loop()

rootx = econsole.winfo_width() + 12
rooty = econsole.winfo_height() + 12
padx = (root.winfo_screenwidth() - rootx) / 2
pady = (root.winfo_screenheight() - rooty) / 2
root.geometry(str(rootx) + 'x' + str(rooty) + '+' + str(int(padx)) + '+' + str(int(pady)))
for child in root.winfo_children(): child.grid_configure(padx = 6, pady = 6)

rootque_loop()

os.system("python ./MiscFunc.py")
from MiscFunc import *

inivars = ['qwdir','getdir','writedbg','offline','retrycnt','spcname','gridfile']
gridvars = ['gridname','homecoord','homeoffx','homeoffy','gridoffx','gridoffy','numofcols','numofrows']

inidir = os.getcwd() + '/QueWay.ini'
haveqwi = root_loop(test_dir,inidir)
if not haveqwi :
	write_debug('Could not find QueWay.ini!')
	do_kill('No QueWay.ini file')

a,b,c = root_loop(load_settings,inidir,inivars)

if a == {} :
	write_debug('Did not get any vars from QueWay.ini!')
	do_kill('No vars loaded')

for i in a :
	globals()[i] = a[i]

spcnames = ['gridinfo'] + b
gridfiles = c

haveqwd = root_loop(test_dir,qwdir,True)
if not haveqwd :
	write_debug('Could not find or make ' + qwdir + '. Starting with offline demo mode!\n')
	offline = True

havgrid = False
for i in range(len(gridfiles)) :
	gridfile = os.getcwd() + '/' + gridfiles[i] + '.ini'
	if not root_loop(test_dir,gridfile) :
		write_debug('Could not find \"' + gridfiles[i] + '\" grid file!\n')
		gridfiles[i] = False
	else :
		gridfiles[i] = root_loop(load_settings,gridfile,gridvars)[0]
		havgrid = True

if not havgrid :
	do_kill('No grid files')


#Load Phases - ToDo: merge this into general data matching
haveps = root_loop(test_dir,'./phases.txt')
if not haveps :
	write_debug('Did not find phases.txt file!')
	do_kill('No phases file')

phases = []
phasefile = open('./phases.txt','r')
for i in phasefile :
	phases = phases + [i.strip()]
phasefile.close


os.system("python ./RMFunc.py")
from RMFunc import *

def do_offline() :

	write_debug('Starting offline mode...\n')
	progat = os.getcwd() + '/offline.exe'
	progat = clean_win_path(progat)
	haveprog = test_dir(progat)
	if not haveprog :
		write_debug('Did not find ' + progat + '!\n')
		do_kill('No offline.exe')

	try :
		pid = sub.Popen(progat, stdin = None, stdout = None, stderr = None, creationflags = sub.CREATE_NEW_CONSOLE).pid
	except :
		write_debug('Exception trying to start offline.exe!\n')
		do_kill('No offline.exe')
	else :
		write_debug('offline.exe started successfully.\n')
	
	time.sleep(3)
	qwdir = os.getcwd() + '/Offline/'
	qwdir = clean_win_path(qwdir)
	havedir = test_dir(qwdir,True)
	
	if not havedir :
		write_debug('Did not find or make ' + qwdir + '!\n')
		do_kill('No offline folder')
	
	globals()['qwdir'] = qwdir
	
	if pid != 0 :
		write_debug('offline.exe started successfully (pid ' + str(pid) + ').\n')
	
	return(pid)

if offline :
	pid = do_offline()

#need to use psutil to kill offline.exe process and children? can't see to do it otherwise.

#Get HELP List (test out RM connect and print list of available commands to debug)
def test_comm() :

	reply = comm1(qwdir,'HELP')
	pid = 0
	
	if offline and reply == [] :
		write_debug('Offline mode failed to reply!\n')
		test_dir(qwdir + 'remote.ask')
		test_dir(qwdir + 'remote.ans')
		do_kill('No reply in offline mode')
	elif reply == [] :
		write_debug('Failed to communicate with RemoteManager at ' + qwdir + '.\n')
		test_dir(qwdir)
		write_debug('Please review configuration. Switching to offline demo mode.\n')
		pid = do_offline()
		globals()['offline'] = True
		test_comm()
	elif offline :
		write_debug('Successfully communicated (offline) with RemoteManager!\n')
	else :
		write_debug('Successfully communicated with RemoteManager!\n')
		
	return(pid)

pid = root_loop(test_comm)

def get_prog_list() :
	#Find "getdir" group in list of directories
	dirs = root_loop(comm1,qwdir,'GET_DIR_LIST')

	okpaths = []
	for a in dirs :
		a = a.casefold()
		b = a.find(getdir)
		if b != -1 :
			okpaths = okpaths + [a]
			write_debug('Found path: ' + str(a) + ' containing: ' + getdir + '\n')

	#Change to each "OK" dir and get part list there
	pathfiles = []
	for a in okpaths :
		root_loop(comm1,qwdir,'CHANGE_PART_DIR\n' + a + '\n')
		#Add a "Check Part Dir" here to make sure it's switched?
		reply = root_loop(comm1,qwdir,'GET_PART_LIST3\n')
		pathfiles = pathfiles + [reply]

	return(pathfiles)

pathfiles = root_loop(get_prog_list)

if len(pathfiles) == 0 :
	write_debug('Did not get any good paths! Switching to offline demo.\n')
	offline = True
	pid = root_loop(do_offline)
	pathfiles = root_loop(get_prog_list)

#ToDo: split program into part and part program to have more than one program per part.
#proglist = {program:{base_path':path,'folder':folder,'img':img.jpg}}

def parse_part_list(plist,mydic) :
	
	a = plist[2:-1]
	b = mydic
	p = plist[0]
	
	for i in a :
		
		if i[0] != "*" :
			c = i.split('\t')
			
			if len(c) == 1 :
				c = c + [p + '/NA/NA.jpg']

			c[1] = clean_win_path(c[1])
			c[1] = c[1].rsplit('/',2)
			c[1] = {'base_path':c[1][0],'folder':c[1][1],'img':c[1][2]}
		else :
			if c[0] == i[2:] :
				b[c[0]] = c[1]
			else :
				d = c[0] + '***' + i[2:]
				b[d] = c[1]
		
	return(b)

proglist = {}
for i in pathfiles :
	proglist = parse_part_list(i,proglist)
	write_debug('Found ' + str(len(proglist)) + ' program paths.\n')

spcdir = qwdir + 'OUT/'
havespcdir = root_loop(test_dir,spcdir,True)
if not havespcdir :
	write_debug('Did not find or make ' + spcdir + '!\n')
	do_kill('no OUT dir')

spcdir = spcdir + 'spc.txt'
rmsg = qwdir + 'REMOTE.MSG'
spcdata = {}


def show_button_img(button_group) :
	
	strvar = button_group[1]
	a = strvar.get()
	if a != '' :
		c = proglist[a]['base_path'] + '/' + proglist[a]['folder'] + '/' + proglist[a]['img']
		d = do_win_path(c)
		d = imgget.open(d)
		d.show()
		write_debug('Displayed large view of: ' + c.rsplit('/', 1)[1] + ' from grid button.\n')
		d.close
	
	return()

def tog_console(*args) :
	
	a = contog.get()
	
	if a :
		econsole.grid_remove()
		contog.set(False)
		write_debug('Hid the console.\n')
	else :
		econsole.grid()
		contog.set(True)
		write_debug('Unhid the console.\n')
		
	return()

def num_valid(entry,length) :
	
	isnum = entry.isdigit()
	if isnum :
		val = entry
	else :
		val = ''
		for i in entry :
			isnum = i.isdigit()
			if isnum :
				val = val + i
	
	if len(val) > length :
		val = val[:length]
	
	write_debug('Checked \"' + entry + '\" is numeric and len <= ' + str(length) + '. Returned '+ val + '.\n')
	return(val)

#Fill the Job Number and Phase Number fields from the barcode when entry in the barcode field happens
#Pass[0]: *args, not used
#Get[0]: "barcode" entry
#Set[0]: "jobnum" based on first 6 digits of "barcode"
#Set[1]: "phasenum" based on next 2 digits of "barcode"
#Return[0]: ()

def bar_entry(*args) :

	code = barcode.get()
	get = num_valid(code,13)
	barcode.set(get)
	a = get[:6]
	b = get[6:8]
	jobnum.set(a)
	phasenum.set(b)
	
	write_debug('Got barcode entry: ' + get + '.\n')
	write_debug('Set job number to: ' + str(a) + ' and set phase number to: ' + str(b) + '.\n')
	return()

def job_entry(*args) :

	a = jobnum.get()
	get = num_valid(a,6)
	jobnum.set(get)
	
	if len(get) > 2 :
		write_debug('Got job number entry: ' + get + '.\n')
	return()

def phase_entry(*args) :

	a = phasenum.get()
	get = num_valid(a,2)
	phasenum.set(get)
	
	if len(get) > 0 :
		write_debug('Got phase number entry: ' + get + '.\n')
	return()

def mach_entry(*args) :

	a = machnum.get()
	get = num_valid(a,4)
	machnum.set(get)
	
	if len(get) > 2 :
		write_debug('Got machine number entry: ' + get + '.\n')
	return()

def sample_entry(*args) :
	
	if len(args) == 0 :
		args = ['none']
	
	hadfoc = samhadfoc.get()
	e = samsize.get()
	havefoc = str(esamsize) == str(root.focus_get())
	
	doman = args[0] != 'reset' and (hadfoc or havefoc)
	
	if doman :
		get = num_valid(e,2)
		samsize.set(get)
		samhadfoc.set(True)
		if len(get) > 0 :
			write_debug('Got user sample size entry: ' + get + '.\n')
	
	elif args[0] == 'set' :
		e = str(int(e) + 1)
		samsize.set(e)
		write_debug('Sample Size set to: ' + e + '.\n')
	
	elif args[0] == 'del' :
		e = str(int(e) - 1)
		samsize.set(e)
		write_debug('Sample Size set to: ' + e + '.\n')
	
	elif args[0] == 'reset' :
		samsize.set(str(0))
		samhadfoc.set(False)
		write_debug('Sample Size reset to: ' + str(0) + '.\n')
	
	return()

def pad_num(val,pad) :

	oldval = val
	if len(val) < pad :
		for i in range(pad - len(val)) :
			val = '0' + val

	if int(val) > 0 :
		write_debug('Padded: ' + str(oldval) + ' to ' + str(val) + '.\n')
	else :
		write_debug('The number: ' + str(val) + ' is not valid.\n')
		val = ''
	
	return(val)

#Get the associated program/s from part number entry. List box shows available
#programs, then user chooses one. Match "proglist" entry in listbox list so
#it can be referenced externally to subprogram.
#Pass[0]: *args, not used
#Get[0]: "partfind" entry
#Set[0]: "proginfo" list based on match
#Set[1]: "proginforef" csv list of "proginfo" reference to "proglist" entry
#Return[0]: ()

def match_partprog(*args) :

	part = str(partfind.get())

	alist = []
	blist = []
	for i in proglist.keys() :
		if i.startswith(part) :
			alist = alist + [i]
		elif part in i :
			blist = blist + [i]
	
	write_debug('Found ' + str(len(alist)) + ' programs starting with \"' + part + '\".\n')
	write_debug('Found ' + str(len(blist)) + ' other programs only containing \"' + part + '\".\n')
	
	#don't bother to list if we have more than a few entries
	if len(alist) > 30 or len(alist) + len(blist) > 60 :
		proginfo.set('')
		selectprog.set('')
		change_state(eproglist,'disabled')
		return()
	
	a = alist + blist
	b = ''
	for i in a :
		b = b + '\"' + i + '\" '
		write_debug(i + '\n')

	proginfo.set(a)
	change_state(eproglist,'normal')
	
	return()


#Do action on listbox select, set imgthumb, and use the current selection to return the proglist
#reference as "selectprog".
#Get[0]: Currently selected program in "eproglist"
#Get[1]: "proginforef" = list of numeric reference to proglist matching entries in "proginfo"
#Set[0]: "selectprog" = numeric reference to specific prog in proglist
#Set[1]: "progimg" = path to currently selected program image
#Set[2]: "imgthumb" assigned image for selected program
#Return[0]: ()

def listbox_select() :

	a = eproglist.get(eproglist.curselection())
	selectprog.set(a)
	write_debug(a + ' is currently selected.\n')
	
	#Set selection image path
	e = proglist[a]['base_path'] + '/' + proglist[a]['folder'] + '/' + proglist[a]['img']
	e = do_win_path(e)
	progimg.set(e)
	write_debug('Image Thumb set to: ' + e + '\n')

	#parse program name into partnum, fullpartnum, and phasename.
	a = a.split('>')[0]
	f = a.split('.')
	
	g = f[0][-6:]
	partnum.set(g)
	
	h = g + '.' + f[1][:3].strip()
	fullpartnum.set(h)
	
	f = a.split(' ')
	for i in f :
		if len(i) == 4 and i in phases :
			phasenam.set(i)
			j = i
	
	write_debug('Set part#: ' + g + ', full part#: ' + h + ' and phase name: ' + j + '.\n')
	
	ebarcode.focus()
	return()

#Set grid button to current selection. Checks first if there is a listbox selection.
#Pass[0]: button group
#Pass[0][0]: Button object
#Pass[0][1]: Button StringVar
#Pass[0][2]: Button Number
#Get[0]: 'progimg' = physical path to image
#Set[0]: button.image to selected program image
#Set[1]: button StringVar = proglist reference number
#Return[0]: ()

def set_button(button_group) :
	button = button_group[0]
	strvar = button_group[1]
	butnum = button_group[2].get()
	write_debug('Button #' + str(butnum) + ' was pressed.\n')
	
	if strvar.get() != '' :
		write_debug('Button is already set to: ' + strvar.get() + '.\n')
		#ToDo : block button click when doing double click so it just opens image?
		#maybe change set to double click and view to single? More clicking, but no confuse?
		#or could I use bind single click instead of button command
		#show_button_img(button_group)
		return()

	if eproglist.curselection() :
		a = progimg.get()
		b = imgget.open(a)
		wsize = button.winfo_width() - 6
		hsize = button.winfo_height() - 6
		b.thumbnail((wsize,hsize),imgget.ANTIALIAS)
		b = ImageTk.PhotoImage(b)
		button.image = b
		button.config(image = b, width = wsize, height = wsize)
		d = selectprog.get()
		strvar.set(d)
		write_debug('Set to part: ' + d + ' and image set to: ' + proglist[d]['img'] + '.\n')
		
		c = holdlist.get()
		if len(c) == 0 :
			c = str(butnum)
		else :
			c = c + '-' + str(butnum)

		holdlist.set(c)
		sample_entry('set')
		
		write_debug('Now holding this/these buttons: ' + c + '.\n')
		
	else :
		write_debug('No program was selected to set.\n')
   
	return()


#Clear the grid button/reset it.
#Pass[0]: button group
#Pass[0][0]: Button object
#Pass[0][1]: Button StringVar
#Pass[0][2]: Button Number
#Set[0]: button.image to default (grid) image
#Set[1]: button StringVar = " "
#Return[0]: ()

def clear_button(button_group) :
	button = button_group[0]
	strvar = button_group[1]
	butnum = button_group[2].get()
	
	state = str(button['state'])
	if state == 'disabled' :
		write_debug('Button #' + str(butnum) + ' was not cleared because it is disabled.\n')
		return()
	
	a = strvar.get()
	if a != '' :
		write_debug('Button #' + str(butnum) + ' was cleared.\n')
		a = imgget.open(clean_win_path(os.getcwd() + '/grid.jpg'))
		wsize = button.winfo_width() - 6
		hsize = button.winfo_height() - 6
		a.thumbnail((wsize,hsize),imgget.ANTIALIAS)
		a = ImageTk.PhotoImage(a)
		button.image = a
		button.config(image = a, width = wsize, height = wsize)
		strvar.set('')

		b = holdlist.get().split(sep = '-')
		c = ''
		if b[0] != '' :
			for i in b :
				if int(i) != butnum :
					if len(c) == 0 :
						c = i
					else :
						c = c + '-' + str(i)

		holdlist.set(c)
		sample_entry('del')
		
		if len(c) == 0 :
			write_debug('Now holding no buttons.\n')
		else :
			write_debug('Now holding this/these buttons: ' + c + '.\n')
		
	return()


def add_que() :
	
	hold = str(holdlist.get())
	gridnums.set(hold)
	
	#Columns: [jobnum, phasenum, controlnum, machnum, samsize, partnum, fullpartnum, phasenam,gridnums]
	#don't have a way to do this as variables at the moment, so hard-coded.
	global spcdata

	jobnum.set(pad_num(jobnum.get(),6))
	phasenum.set(pad_num(phasenum.get(),2))
	machnum.set(pad_num(machnum.get(),4))
	
	e = [gridnums.get(),jobnum.get(),phasenum.get(),controlnum.get(),machnum.get(),samsize.get(),partnum.get(),fullpartnum.get(),phasenam.get()]
	
	queok = True
	g = 0
	for i in e :
		if i == '' :
			queok = False
			write_debug('NG! ' + spcnames[g] + ': ' + str(i) + '.\n')
		else :
			write_debug('OK! ' + spcnames[g] + ': ' + str(i) + '.\n')
		g += 1
	
	if queok :

		b = ''
		for i in hold.split(sep = '-') :
			change_state(buttlist[int(i)][0],'disabled')
			if b == '' :
				b = buttlist[int(i)][1].get()
		
		d = b + '>' + hold
		c = d + '>FRESH'
		
		equelist.insert(tk.END,c)
		holdlist.set('')
		sample_entry('reset')
		barcode.set('')
		jobnum.set('')
		phasenum.set('')
		controlnum.set(2)
		machnum.set('')
		
		write_debug('Passed hold (' + d + ') to que, cleared SPC values, and set buttons to disabled.\n')
		
		spcdata[d] = {}
		eloc = 0
		for i in spcnames :
			spcdata[d][i] = e[eloc]
			eloc += 1

		samhadfoc.set(False)
		
	else :
		gridnums.set('')
	
	
	#what was I trying to do with this?
	#    if equelist.curselection() == '' :
	#        equelist.activate(0)
	
	return()


def del_que(a) :
	
	b = str(equelist.get(a))
	b = b.split(sep = '>')
	for i in b[1].split(sep = '-') :
		change_state(buttlist[int(i)][0],'normal')
		clear_button(buttlist[int(i)])
		sample_entry('set')

	b = equelist.get(a)
	equelist.delete(a)
	c = b.split(sep = '>')
	
	global spcdata
	spcdata.pop(str(c[0] + '>' + c[1]), None)
	
	write_debug('Que selection #' + str(a) + '(' + b + ') was deleted.\n')

	return()


def que_check(*args) :
	
	a = equelist.size()
	b = playtog.get()
	
	if a == 0 :
		change_state(edel,'disabled')
		change_state(eplay,'disabled')
	elif not b :
		change_state(edel,'normal')
		change_state(eplay,'normal')

	write_debug('Que is: ' + str(equelist.get(0,tk.END)) + '.\n')
	
	return()


def hold_check(*args) :
	
	a = len(holdlist.get())

	if a == 0 :
		change_state(eproglist,'normal')
		change_state(eque,'disabled')
		change_state(epartfind,'normal')
	else :
		change_state(eproglist,'disabled')
		change_state(eque,'normal')
		change_state(epartfind,'disabled')
	
	return()


def change_state(obj,state) :
	
	a = state
	b = str(obj['state'])
	
	try :
		c = str(obj.config().get('text')[-1]) + ' '
	except :
		c = ''
	
	if a != b :
		obj.config(state = a)
		write_debug('The ' + c + 'object state was switched to: ' + a + '.\n')

	return()


def que_update(loc,state) :

	a = equelist.get(loc).split(sep = '>')
	b = a[0] + '>' + a[1]
	done = b + '>' + state

	c = playtog.get()

	if c :
		equelist.delete(loc)
		equelist.insert(loc, done)
		write_debug('Changed ' + b + '>' + a[2] + ' to ' + done + '.\n')
	else :
		write_debug('Que was stopped before changing ' + b + '>' + a[2] + ' to ' + done + '.\n')

	return()


def que_next():
	
	quenow = quefrom.get()
	write_debug('quenow was ' + str(quenow - 1) + '\n')
	write_debug('equelist size is ' + str(equelist.size()) + '\n')
	quenow += 1
	
	if quenow > equelist.size() :
		write_debug('Looping to top of que.\n')
		quenow = 0
		
	quefrom.set(quenow)
	write_debug('quenow is ' + str(quenow) + '\n')
	
	return()
	
	
def play_que(*args) :

	if equelist.size() == 0 :
		write_debug('Nothing in Que to run...\n')
		que_next()
		playtog.set(False)
	
	tog = playtog.get()
	
	if tog :
		
		change_state(eplay,'disabled')
		change_state(epause,'normal')
		change_state(edel,'disabled')

		run = runinfo.get()
		write_debug('Que is running. Que run state: ' + run + '.\n')

		quenow = quefrom.get()
		write_debug('loop quenow is ' + str(quenow) + '\n')
		write_debug('loop equelist size is ' + str(equelist.size()) + '\n')
		write_debug('loop equelist.get is ' + str(equelist.get(quenow)) + '\n')
		
		if quenow >= equelist.size() :
			que_next()
			quenow = quefrom.get()
		
		playwat = equelist.get(quenow)
		a = playwat.split(sep = '>')
		write_debug('Starting next in que: ' + playwat + ' .\n')
		
		if a[2] != 'DONE' :
			
			neednew = a[2] == 'FRESH' or a[2] == 'ERROR'
			if run == 'READY' and neednew :
				
				que_update(quenow,'ACTIVE')
				d = a[1].split(sep = '-')
				e = buttlist[int(d[0])][1].get()
				g = proglist[e]['base_path']
				msg = 'CHANGE_PART_DIR\n' + g + '\n'
				print('msg is:' + msg + '\n')
				reply = root_loop(comm1,qwdir,msg)

				if len(reply) != 0 :
					if reply[0] == 'OK' :

						spc = spcdata[str(a[0] + '>' + a[1])]
						write = []
						index = 0
						for i in spc.keys() :
							
							if index <= 9 :
								qwdat = 'QWDat0' + str(index)
							else :
								qwdat = 'QWDat' + str(index)
							
							write = write + [qwdat + '=' + i + '>' + str(spc[i])]
							index += 1
							
						root_loop(write_file,write,spcdir,True)
						
						#Columns: [jobnum, phasenum, controlnum, machnum, samsize, partnum, fullpartnum, phasenam,gridnums]
						sublot = spc['jobnum'] + spc['phasenum'] + '00000' + spc['machnum'] + str(spc['controlnum'])
						write_debug('Using sublot string: \"' + sublot + '\".\n')
						
						#ToDo: 1st e = part name, 2nd e = part program name
						msg = 'EXECUTE_PATH_PART_PROGRAM \n'
						msg = msg + g + '\n'
						msg = msg + e + '\n' + e + '\n' + str(0) + '\n' + str(0) + '\n'
						msg = msg + gridfiles[0]['homecoord'] + '\n' + str(len(d)) + '\n'
						msg = msg + str(1) + '\n' + sublot + '\n'
						reply = root_loop(comm1,qwdir,msg)

						if len(reply) != 0 :
							if reply[0] == 'OK' :
								que_update(quenow,'RUNNING')
								runinfo.set('RUN')
							else :
								que_update(quenow,'ERROR')
								write_debug('Got ' + reply + ' instead of \"OK\".\n')
						else :
							que_update(quenow,'ERROR')
					else :
						que_update(quenow,'ERROR')
						write_debug('Got ' + reply + ' instead of \"OK\".\n')
				else :
					que_update(quenow,'ERROR')

			elif run == 'RUN' and a[2] == 'RUNNING' :
				g = root_loop(wait_read,rmsg,True)
				
				write_debug('the result of read file is: ' + str(g) + '.\n')
				if len(g) != 0 :
					runinfo.set(g[0])

				write_debug('Currently running ' + a[0] + '.\n')

			elif run == 'PPEND' and a[2] == 'RUNNING' :
				que_update(quenow,'DONE')
				runinfo.set('READY')
				write_debug(a[0] + ' ran successfully.\n')

			elif run == 'PPERR' and a[2] == 'RUNNING' :
				que_update(quenow,'ERROR')
				write_debug(a[0] + ' did not run successfully!\n')
			
			#elif a[2] == 'FATAL' :
				#write_debug('The program, ' + playwat + ' is FATAL and will be skipped!\n')
			
			#elif run != 'READY' :
				#write_debug('Reply ' + str(run) + ' is unknown! Stopping the que.\n')
				#que_update(quenow,'FATAL')
				#runinfo.set('READY')
				#playtog.set(False)
		
		else :
			write_debug('Congrats, ' + playwat + ' is already DONE!\n')
		
		que_next()
		root.after(2000, lambda b=b : play_que())
		
	else :
		change_state(epause,'disabled')
		if equelist.size() != 0 :
			change_state(eplay,'normal')
			change_state(edel,'normal')
		quefrom.set(0)
		write_debug('Que is not running. Quenow reset to 0.\n')
		
	return()


#3 panes/frames in root for entry area, button grid area, and que/run area
entryf = ttk.Frame(root)
entryf.grid(column = 0, row = 0, sticky = (tk.N, tk.E, tk.W))

buttonf = ttk.Frame(root)
buttonf.grid(column = 1, row = 0, rowspan = 2, sticky = (tk.N, tk.E, tk.W))

quef = ttk.Frame(root)
quef.grid(column = 2, row = 0, rowspan = 2, sticky = (tk.N, tk.E, tk.W))

#barcode = StringVar()
#jobnum = StringVar()
#phasenum = StringVar()
#controlnum = IntVar() - selection variable for radiobuttons CIS/CRP/CFF/None
#machinenum = StringVar()
#samsize = StringVar() - lot sample size
#partnum = StringVar()
#fullpartnum = StringVar()
#phasenam = StringVar()
#gridnums = StringVar()

#partfind = StringVar() - part program search box (by part number)
#selectprog = StringVar() - what is currently selected in prog select list
#proginfo = StringVar() (listvar) - list of prog names based on prog number entry
#progimg = StringVar() - path of image matching current selection
#holdlist = StringVar() - set of buttons for current selection (before que)
#quelist = StringVar() (listvar) - list of que'd programs to run
#contog = BooleanVar() - console toggle on or off
#playtog = BooleanVar() - que play/pause on or off
#runinfo = StringVar() - status of que (READY,RUN>[prog],PPEND,PPERR)
#quefrom = IntVar() - what is the current que to run (if error in [0], run [1])
#samhadfoc = BooleanVar() - set when sample entry has gotten focus to stop using set buttons for qty.

blank = ttk.Label(entryf, text = '')
blank.grid(column = 0, row = 0, columnspan = 2)

partfind = tk.StringVar()
lpartfind = ttk.Label(entryf, text = 'Part Number')
lpartfind.grid(column = 0, row = 1, sticky = (tk.E))
epartfind = ttk.Entry(entryf, textvariable = partfind)
epartfind.grid(column = 1, row = 1, sticky = (tk.E, tk.W))
partfind.trace('w', match_partprog)

#list of programs that match current search, selection in this list is whatever program to que
#Todo: change this to set correctly like the que list using get/put instead of writing to the listvar

selectprog = tk.StringVar()
progimg = tk.StringVar()
proginfo = tk.StringVar()
eproglist = tk.Listbox(entryf, listvariable = proginfo, state = 'disabled', exportselection = False, width = 30)
eproglist.grid(column = 0, row = 2, columnspan = 2, sticky = (tk.E, tk.W))
eproglist.bind('<<ListboxSelect>>', lambda a=a : listbox_select())

blank = ttk.Label(entryf, text = '')
blank.grid(column = 0, row = 3, columnspan = 2)

#Todo: make these configurable in .ini to add/remove, and parse contents.
partnum = tk.StringVar()
fullpartnum = tk.StringVar()
phasenam = tk.StringVar()
gridnums = tk.StringVar()

barcode = tk.StringVar()
lbarcode = ttk.Label(entryf, text = 'Barcode')
lbarcode.grid(column = 0, row = 6, sticky = (tk.W))
ebarcode = ttk.Entry(entryf, textvariable = barcode)
ebarcode.grid(column = 0, row = 7, sticky = (tk.W, tk.E))
barcode.trace('w', bar_entry)

jobnum = tk.StringVar()
ljobnum = ttk.Label(entryf, text = 'Job Number')
ljobnum.grid(column = 0, row = 8, sticky = (tk.W))
ejobnum = ttk.Entry(entryf, textvariable = jobnum)
ejobnum.grid(column = 0, row = 9, sticky = (tk.E, tk.W))
jobnum.trace('w', job_entry)

machnum = tk.StringVar()
lmachnum = ttk.Label(entryf, text = 'Machine Number')
lmachnum.grid(column = 0, row = 10, sticky = (tk.W))
emachnum = ttk.Entry(entryf, textvariable = machnum)
emachnum.grid(column = 0, row = 11, sticky = (tk.E, tk.W))
machnum.trace('w', mach_entry)

phasenum = tk.StringVar()
lphasenum = ttk.Label(entryf, text = 'Phase Number')
lphasenum.grid(column = 1, row = 8, sticky = (tk.W))
ephasenum = ttk.Entry(entryf, textvariable = phasenum)
ephasenum.grid(column = 1, row = 9, sticky = (tk.E, tk.W))
phasenum.trace('w', phase_entry)

#This is set to not take tab-focus so uses # of set buttons until user gives it focus.
#Then it stops updating from buttons and uses whatever user entered.
samsize = tk.StringVar()
samsize.set('0')
samhadfoc = tk.BooleanVar()
samhadfoc.set(False)
lsamsize = ttk.Label(entryf, text = 'Sample Size')
lsamsize.grid(column = 1, row = 10, sticky = (tk.W))
esamsize = ttk.Entry(entryf, textvariable = samsize, takefocus = 0)
esamsize.grid(column = 1, row = 11, sticky = (tk.E, tk.W))
samsize.trace('w', sample_entry)
esamsize.bind("<1>", lambda a = a : sample_entry())

#ToDo : make this frame tab-into-able, but not each button. Use arrows to change selected button.
controlf = ttk.Frame(entryf)
controlf.grid(column = 1, row = 6, rowspan = 2, sticky = (tk.S))
controlnum = tk.IntVar()
controlnum.set(2)
econa = ttk.Radiobutton(controlf, text = 'CIS', width = -6, value = 1, variable = controlnum)
econa.grid(column = 0, row = 0, sticky = (tk.E, tk.W))
econb = ttk.Radiobutton(controlf, text = 'CRP', width = -6, value = 2, variable = controlnum)
econb.grid(column = 0, row = 1, sticky = (tk.E, tk.W))
econc = ttk.Radiobutton(controlf, text = 'CFF', width = -6, value = 3, variable = controlnum)
econc.grid(column = 1, row = 0, sticky = (tk.E, tk.W))
econd = ttk.Radiobutton(controlf, text = 'None', width = -6, value = 4, variable = controlnum)
econd.grid(column = 1, row = 1, sticky = (tk.E, tk.W))

#Generate rows with buttons. Bake in the lambda commands on creation so each button is it's own reference.
#Make buttlist with each "button" as [button obj, stringvar, button num intvar]
#Todo : make this configurable shape and quantity, with .ini vars to define grid and XY offsets

#gridvars = ['gridname','homecoord','homeoffx','homeoffy','gridoffx','gridoffy','numofcols','numofrows']

def make_grid(a,b) :

	grid = a[b]
	buttqty = int(grid['numofcols']) * int(grid['numofrows'])
	b = 0
	c = int(grid['numofrows']) * 2
	g = c
	
	buttlist = []
	for a in range(buttqty) :
		strvar = tk.StringVar()
		buttonnum = tk.IntVar()
		button = tk.Button(buttonf, textvariable = strvar)

		d = imgget.open(clean_win_path(os.getcwd() + '/grid.jpg'))
		d.thumbnail((65,65),imgget.ANTIALIAS)
		d = ImageTk.PhotoImage(d)
		button.image = d
		button.config(image = d)

		button.grid(column = b, row = (c - 1))
		buttonnum.set(a)
		
		xis = tk.IntVar()
		e = int(grid['homeoffx']) + (int(grid['gridoffx']) * b)
		xis.set(e)
		
		yis = tk.IntVar()
		f = int(grid['homeoffy']) + int(int(grid['gridoffy']) * ((g - 1) - (c - 1)) / 2)
		yis.set(f)
		
		d = [button,strvar,buttonnum,xis,yis]

		button['command'] = lambda d = d : set_button(d)
		#Have to set b=b because bind always passes the action?
		button.bind('<3>', lambda b = b, d = d : clear_button(d))
		button.bind('<Double-1>', lambda b = b, d = d : show_button_img(d))

		buttlist = buttlist + [d]
		
		label = ttk.Label(buttonf, text = 'Grid #' + str(a + 1) + ': ' + str(e) + 'x' + str(f))
		label.grid(column = b, row = c)

		if a <= int(grid['numofcols']) :
			blank = ttk.Label(buttonf, text = '')
			blank.grid(column = b, row = 0)

		b += 1
		if b > int(grid['numofcols']) - 1 :
			b = 0
			c -= 2

	return(buttlist)

gridselect = 0
buttlist = make_grid(gridfiles,gridselect)
root.update()

blank = ttk.Label(quef, text = '')
blank.grid(column = 0, row = 0, columnspan = 2)        

#after select prog, click a grid button(s) to 'hold' them as a group, then press que to add that 
#set to the queue list. spcdata will be matched to each que with index set as prog name>grid#-grid#

eque = ttk.Button(quef, text = 'Queue', state = 'disabled', command = lambda a=a : add_que())
eque.grid(column = 0, row = 6, sticky = (tk.E, tk.W))

edel = ttk.Button(quef, text = 'Delete', state = 'disabled', command = lambda a=a : del_que(int(equelist.curselection()[0])))
edel.grid(column = 1, row = 6, sticky = (tk.E, tk.W))

holdlist = tk.StringVar()
holdlist.trace('w', hold_check)
quelist = tk.StringVar()
quelist.trace('w', que_check)
equelist = tk.Listbox(quef, listvariable = quelist, exportselection = False, width = 40)
equelist.grid(column = 0, row = 7, columnspan = 2, sticky = (tk.E, tk.W))

#Play and Pause buttons for running the programs out of the queue.

playtog = tk.BooleanVar()
playtog.set(False)
runinfo = tk.StringVar()
runinfo.set('READY')
quefrom = tk.IntVar()
quefrom.set(0)
epause = ttk.Button(quef, text = 'Pause', state = 'disabled', command = lambda : playtog.set(False))
epause.grid(column = 0, row = 8, sticky = (tk.E, tk.W))
eplay = ttk.Button(quef, text = 'Play', state = 'disabled', command = lambda : playtog.set(True))
eplay.grid(column = 1, row = 8, sticky = (tk.E, tk.W))
playtog.trace('w', play_que)

blank = ttk.Label(entryf, text = '')
blank.grid(column = 0, row = 9, columnspan = 2)

contog = tk.BooleanVar()
contog.set(True)
econtog = ttk.Button(quef, text = 'Console', command = lambda a=a : tog_console())
econtog.grid(column = 0, row = 11, sticky = (tk.E, tk.W))

equit = ttk.Button(quef, text = 'Quit', command = lambda a=a : do_kill('Quit button'))
equit.grid(column = 1, row = 11, sticky = (tk.E, tk.W))

#get first console data and load into new console

save = econsole.get('1.0',tk.END + '-1c')
econsole.destroy()
econsole = tk.Text(root, height = 6, exportselection = False, wrap = tk.NONE)
econsole.grid(column = 0, row = 2, columnspan = 3, sticky = (tk.S, tk.E, tk.W), padx = 6, pady = 6)
for i in save :
	econsole.insert(tk.END,i)
econsole.see(tk.END)

#define weights of columns/rows for window re-sizing, and padding, min window size etc.
	
grids = [root, entryf, buttonf, quef]

for i in grids :
	for j in range(i.grid_size()[0]): i.columnconfigure(j, weight = 1)
	for j in range(i.grid_size()[1]): i.rowconfigure(j, weight = 0)

root.columnconfigure(1, weight = 4)
root.rowconfigure(0, weight = 0)
	
for child in entryf.winfo_children(): child.grid_configure(padx = 4, pady = 4)
for child in buttonf.winfo_children(): child.grid_configure(padx = 1, pady = 1)
for child in quef.winfo_children(): child.grid_configure(padx = 4, pady = 4)

root.minsize(1280,720)
root.maxsize(root.winfo_screenwidth()-10,root.winfo_screenheight()-10)
root.geometry('1280x720')

mainloop = True
epartfind.focus()
root.mainloop()
