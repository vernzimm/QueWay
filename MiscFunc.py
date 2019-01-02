from __main__ import *


def load_settings(watfile,watvars) :
    
    b = {}
    c = []
    d = []
    e = watfile.split(sep = '\\')[-1]
    
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
                    else :
                        b[k] = j[1]
    
    file.close()
    return(b,c,d)
