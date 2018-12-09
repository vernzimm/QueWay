from __main__ import *

#Watch for a file
#Pass [0]: file path variable
#Returns [0]: True or False file was found

def have_file(file) :
    
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
        debug = 'have file: ' + file + ' after ' + d + ' seconds.\n'
    else :   
        debug = 'do not have file: ' + file + ' after ' + d + ' seconds.\n'
        
    write_debug(debug)
    return(get)


#Delete a file
#Pass [0]: file path variable
#Return [0]: True or False did delete file (under 3 seconds)

def delete_file(file) :
    
    did = not os.path.isfile(file)
    
    if did :
        debug = 'did not find: ' + file + ' to delete.\n'
        write_debug(debug)
        return(did)

    a = 0
    while os.path.isfile(file) and a <= 3 :
        try :
            os.remove(file)
        except OSError :
            time.sleep(0.01)
        a += 0.01

    a = str(round(a,2))
    
    did = not os.path.isfile(file)
    if did :
        debug = 'did delete: ' + file + ' after ' + a + ' seconds.\n'
    else :
        debug = 'could not delete: ' + file + ' after ' + a + ' seconds and file exists = ' + str(os.path.isfile(file)) + '.\n'

    write_debug(debug)
    return(did)


#Try to open file in append mode and read the first 8 characters.
#Pass[0]: file path variable
#Return[0]: True or False file was locked

def is_locked(file):
    
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
        debug = file + ' is still locked after ' + d + ' seconds.\n'
    else :
        debug = file + ' is not locked after ' + d + ' seconds.\n'

    write_debug(debug)
    return (locked)


#Read in a file and delete after if needed
#Pass [0]: file path variable
#Pass [1]: True or False delete the file
#Return [0]: cleaned file data

def read_file(file,delete) :
    
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
            #scrub the '/n's
            e = i[:-1]
            data = data + [e]
            a += 1
        b.close()
        debug = 'Did read ' + str(a) + ' lines from: ' + file + '.\n'
    except OSError :
        debug = 'Did not read ' + file + ' and exists = ' + str(os.path.isfile(file)) + '.\n'
    
    if delete :
        delete_file(file)
    else :
        debug = debug + 'Did not attempt to delete ' + file + 'and exists = ' + str(os.path.isfile(file)) + '.\n'
    
    write_debug(debug)
    return(data)


#Do comm1 one style command (rask->rans)
#Pass[0]: RM command
#Return[0]: RM answer data

def comm1(command) :
    
    delete_file(rans)
    
    cmd = open(rask,'w')
    cmd.write(command)
    cmd.close()
    
    debug = 'Wrote: ' + command + ' to ' + rask + '.\n'
    
    reply = read_file(rans,True)
    
    if reply != [] :
        debug = debug + 'Completed command: ' + command + '.\n'
        line = 1
        for i in reply :
            debug = debug + 'rans line ' + str(line) + ': ' + i + '\n'
            line += 1
    else :
        debug = debug + 'Did not complete command: ' + command + ' successfully.\n'
    
    write_debug(debug)
    return(reply)
