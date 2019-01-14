from __main__ import *

#Watch for a file
#Pass [0]: file path variable
#Returns [0]: True or False file was found

def have_file(file) :

	file = clean_win_path(file)
	b = 0
	d = 0
	while b <= 500 :
		get = os.path.isfile(file)
		if get == True :
			break
		time.sleep(0.01)
		d += 0.01
		b += 1
	d = str(round(d,2))
	
	if get == True :
		write_debug('have file: ' + file + ' after ' + d + ' seconds.\n')
	else :   
		write_debug('do not have file: ' + file + ' after ' + d + ' seconds.\n')
		
	return(get)


#Delete a file
#Pass [0]: file path variable
#Return [0]: True or False did delete file (under 3 seconds)

def delete_file(file) :

	file = clean_win_path(file)
	did = not os.path.isfile(file)
	
	if did :
		write_debug('did not find: ' + file + ' to delete.\n')
		
		return(did)

	a = 0
	while os.path.isfile(file) and a <= 1 :
		try :
			os.remove(file)
		except OSError :
			time.sleep(0.01)
		a += 0.01
		
	a = str(round(a,2))
	
	did = not os.path.isfile(file)
	if did :
		write_debug('did delete: ' + file + ' after ' + a + ' seconds.\n')
	else :
		write_debug('could not delete: ' + file + ' after ' + a + ' seconds and file exists = ' + str(os.path.isfile(file)) + '.\n')

	return(did)


#Try to open file in append mode and read the first 8 characters.
#Pass[0]: file path variable
#Return[0]: True or False file was locked

def is_locked(file):
	
	file = clean_win_path(file)
	locked = True
	d = 0
	while locked and d < 3 :
		try:
			a = open(file, 'a', 8)
			if a :
				locked = False
				a.close()
		except IOError:
			locked = True
			time.sleep(0.01)
		d += 0.01

	d = str(round(d,2))
	
	if locked :
		write_debug(file + ' is still locked after ' + d + ' seconds.\n')
	else :
		write_debug(file + ' is not locked after ' + d + ' seconds.\n')

	return (locked)


#Read in a file and delete after if needed
#Pass [0]: file path variable
#Pass [1]: True or False delete the file
#Return [0]: cleaned file data

def read_file(file,delete) :
	
	file = clean_win_path(file)
	data = []
	
	got = have_file(file)
	if got == False :
		return(data)
	
	lock = is_locked(file)
	if lock :
		return(data)
	
	a = 0
	try :
		b = open(file,'r')
		for i in b :
			e = i.rstrip()
			data = data + [e]
			a += 1
		b.close()
		write_debug('Did read ' + str(a) + ' lines from: ' + file + '.\n')
	except OSError :
		write_debug('Did not read ' + file + ' and exists = ' + str(os.path.isfile(file)) + '.\n')
	
	if delete :
		delete_file(file)
	else :
		write_debug('Did not attempt to delete ' + file + ' and exists = ' + str(os.path.isfile(file)) + '.\n')
	
	return(data)


#Wait loop to read a file using read_file. Args are passed thru directly.
#Pass [0]: file path variable
#Pass [1]: True or False delete the file
#Return [0]: returned file data

def wait_read(file,delete) :
	
	file = clean_win_path(file)
	result = []
	while result == [] :
		result = read_file(file,delete)
		time.sleep(1)

	rootque.put('kill')
	return(result)
	

#Do comm1 one style command (rask->rans)
#Pass[0]: Directory to use to communicate
#Pass[1]: RM command
#Return[0]: RM answer data

def comm1(commloc,command) :
	
	retries = retrycnt
	commloc = clean_win_path(commloc)
	rask = commloc + 'REMOTE.ASK'
	rans = commloc + 'REMOTE.ANS'
	
	command = command + '\n'
	
	while retries > 0 :
		delete_file(rans)

		cmd = open(rask,'w')
		cmd.write(command)
		cmd.close()

		cmdis = command.splitlines()[0]

		write_debug('Wrote command: ' + cmdis + ' to ' + rask + '.\n')

		line = 1
		for i in command.splitlines() :
			write_debug('rask line ' + str(line) + ': ' + i + '\n')
			line += 1

		reply = read_file(rans,True)

		if reply != [] :
			a = retrycnt - (retries - 1)
			write_debug('Completed command: ' + cmdis + ' after ' + str(a) + ' tries.\n')
			line = 1
			for i in reply :
				write_debug('rans line ' + str(line) + ': ' + i + '\n')
				line += 1
			retries = 0
		else :
			write_debug('Did not complete command: ' + cmdis + ' successfully.\n')
			retries -= 1
			write_debug('Retrying ' + str(retries) + ' more times!\n')

	rootque.put('kill')
	return(reply)


#Write a file (misc, no specific format). Writes a tmp file first to complete, then copies.
#Pass[0]: File data as a list
#Pass[1]: Directory to write, including file name
#Pass[2]: optional : True or False to delete the file if it already exists

def write_file(what,where,delete=False) :
	
	where = clean_win_path(where)
	if delete :
		delete_file(where)
	
	tmp = where.rsplit('/',1)
	tmp = tmp[0] + '/temp' + tmp[1]
	
	line = 1
	cmd = open(tmp,'w')
	for i in what :
		cmd.write(str(i) + '\n')
		write_debug('rans line ' + str(line) + ': ' + i + '\n')
		line += 1
	cmd.close()
	
	copy(tmp,where)
	delete_file(tmp)

	write_debug('Wrote file: ' + where + '.\n')
	return()
