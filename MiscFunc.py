from __main__ import *

#This function loads a given file and parses variables QueWay.ini and Grid.txt stored in ./
#ToDo: Make this generic...
#Pass[0]: file path including extension
#Pass[1]: list of variable names that will match the incoming variables
#Return[0]: dictionary matched variable pairs
#Return[1]: special case "spcname"
#Return[2]: special case "gridname"

def load_settings(watfile,watvars) :
	
	test_dir(watfile)
	watfile = clean_win_path(watfile)
	e = watfile.rsplit('/',1)[1]
	
	b = {}
	c = []
	d = []
	
	try :
		file = open(watfile,'r')
	except :
		write_debug('Was not able to open the settings file \"' + e + '\"!\n')
		return(b,c,d)
	
	a = 1
	for i in file.readlines() :
		i = i.strip()
		if len(i) != 0 and i[0] != '#' :

			write_debug(e + ' entry#' + str(a) + ': ' + i + '\n')
			a += 1

			j = i.split(sep = '=')
			for k in range(len(j)) :
				j[k] = j[k].strip()

			for k in watvars :
				if j[0] == k :
					if k == 'spcname' :
						c = c + [j[1]]
					elif k == 'gridfile' :
						d = d + [j[1]]
					elif k == 'retrycnt' :
						b[k] = int(j[1])
					elif j[1] == 'True' :
						b[k] = True
					elif j[1] == 'False' :
						b[k] = False
					else :
						b[k] = j[1]
	
	file.close()
	return(b,c,d)


#Check a directory or file exists, and make it if requested (make path up to file).
#Changes "\\" to "/" so using "./" or ".\\" is OK. If want to make a folder with "." in name (i.e. ./Prog V1.0 Folder)...
#Enclose with "/" after (i.e. ./Prog V1.0 Folder/)
#Pass[0]: directory or file path (differentiates by existence of file.ext at end of path)
#Pass[1]: True or False to make the file or path if it doesn't exist
#Return[0]: True or False exists (assumed was made if didn't exist etc)

def test_dir(watpath,domake=False) :
	
	b = clean_win_path(watpath)
	
	a = b.rsplit('/',1)[1]
	a = a.split(sep = '.')
	
	dopath = True
	if len(a) > 1 and a[1] != '' :
		dopath = False

	a = os.path.exists(b)
		
	if a :
		write_debug('\"' + b + '\" already exists.\n')
		have = True
	elif domake :
		try :
			if dopath :
				write_debug('trying to make the path \"' + b + '\"\n')
				c = ''
				for i in b.split('/') :
					c = c + i + '/'
					if not test_dir(c) :
						d = c.rsplit('/',1)[0]
						e = test_dir(d)
						if e :
							write_debug('A file \"' + d + '\" exists and a folder \"' + c + '\" can not be made!\n')
							raise
						else :
							os.makedirs(c)
			else :
				a = b.rsplit('/', 1)[0] + '/'
				a = test_dir(a,True)
				if a :
					write_debug('trying to make the file \"' + b + '\"\n')
					file = open(b,'w')
					file.close
		except :
			write_debug('Failed to make \"' + b + '\"!\n')
			have = False
		else :
			write_debug('\"' + b + '\" did not exist, but was made successfully.\n')
			have = True
	else :
		write_debug('\"' + b + '\" does not exist and did not try to make.\n')
		have = False

	return(have)
	
	
#Change backslash to forward for path strings
#Pass[0]: path
#Return[0]: cleaned path
def clean_win_path(inpath) :

	b = ''
	for i in inpath :
		if i == '\\' :
			b = b + '/'
		else :
			b = b + i
		
	return(b)
	
#Change backslash to forward for path strings
#Pass[0]: path
#Return[0]: windows'd path
def do_win_path(inpath) :

	b = ''
	for i in inpath :
		if i == '/' :
			b = b + '\\'
		else :
			b = b + i
		
	return(b)

#Kill/quit application
#Pass[0]: String of reason for killing(optional)
def do_kill(method='error') :

	time.sleep(1)
	write_debug('The program will now close! Reason: ' + method + '.\n')
	time.sleep(0.05)
	
	try :
		root.destroy()
	except :
		pass
		
	exit()
