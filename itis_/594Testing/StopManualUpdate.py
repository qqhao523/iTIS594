##### just for stop the running updtate thread######
###### for pit use: if the pit is time out, stop the update########
from TestApp import *

STOP_MANUALUPDATE_COMMAND=15

if __name__=="__main__":

    nRet=Test_TmccSendCommand(STOP_MANUALUPDATE_COMMAND,None,None)

    print nRet
    
    



    

