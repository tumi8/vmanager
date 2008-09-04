
import logging
import sys


__logger = None



def logger():
    return  __logger


def init(appname, logfile, tostderr):
    global __logger  #IGNORE:W0603
    __logger = logging.getLogger(appname)
    __logger.handlers = []
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    if logfile is not None and logfile != "":
        hdlr = logging.FileHandler(logfile)    
        hdlr.setFormatter(formatter)
        __logger.addHandler(hdlr)
    if tostderr:
        hdstd = logging.StreamHandler(sys.stderr)
        hdstd.setFormatter(formatter)
        __logger.addHandler(hdstd)
    
    __logger.setLevel(logging.DEBUG)