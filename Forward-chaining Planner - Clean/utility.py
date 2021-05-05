import datetime
import copy
import os
import re

def zeroStringPad(input_str:str, new_length:int):
    output_str = copy.deepcopy(str(input_str))
    while len(output_str) < new_length:
        output_str = "0" + output_str
    return output_str
    
def listExtend(main_list:list, extension_list:list):
    for someelement in extension_list:
        if not(someelement in main_list):
            main_list.append(someelement)

def smallify(somestring):
    output = somestring.lower()
    output = output.replace(" ","_")
    output = re.sub('[^0-9a-zA-Z]+', '', output)
    
    return output
    
def listRemove(main_list:list, removal_list:list):
    for someelement in removal_list:
        try:
            main_list.remove(someelement)
        except Exception:
            pass
    return main_list
    
def log(logfilename, logstr, mode1, enabled=True, header=None):

    if enabled:
        
        if (not os.path.exists(logfilename)) and (header is not None):
            logfile = open(logfilename, "a+")
            logfile.write(header + "\n")
            logfile.close()
        
        logfile = open(logfilename, "a+")
        now = datetime.datetime.now()

        if mode1 == "line/txt":
            logfile.write(str(datetime.datetime.now()) + " " + logstr + "\n")
            
        elif mode1 == "line/csv":
            logfile.write(str(datetime.datetime.now()) + "," + logstr + "\n")
        else:
            raise Exception("[!!!] ERROR: Invalid mode1: " + str(mode1))
        logfile.close()    
