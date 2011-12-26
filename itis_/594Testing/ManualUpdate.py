#This file is used for the automation test for manual update function.
################ Function name: Manual update#####################
################ Author: Zhouyanping         #####################
################ Date:  2008-9-23            #####################
###File name: ManualUpdate.py

from TestApp import *
from CurrentPatternVersion import *
import time
import ReadLogInfo
import inspect
import os
import signal

MAX_EXE_COUNT=20000

NONEED_UPDATE=10204

USER_CANCEL=10210

NET_ERROR=10228

LOG_STRING="iTIS_1.5-DEBUG_LOG"

DEBUG_RELEVANT_PATH="./PIT/logs/Debug"

DEBUG_LOG_PATH=os.path.abspath(DEBUG_RELEVANT_PATH)

G_DEBUG_File=None

Module_Name="ManualUpdate.py"

RunningStatus=0

def WriteDebugLogFile(msg,filename,linenum,level):

    global G_DEBUG_File

    ltime=time.localtime()

    nYear=ltime.tm_year

    tYear=str(nYear)

    tYear=tYear[2:4]

    nMonth=ltime.tm_mon

    nDay=ltime.tm_mday

    nHour=ltime.tm_hour

    nMin=ltime.tm_min

    nSec=ltime.tm_sec

    if level<=10:

        strType='sss'

    elif level<=30:

        strType="www"
    else:

        strType='iii'



    G_DEBUG_File.write("%s/%d/%d %d:%d:%d <%s> %s (%s:%d)\n" %(nYear,nMonth,nDay,nHour,nMin,nSec,\
                                                                  strType,msg,filename,linenum))





def GetDebugLogFile():


    strLine=time.strftime("%g%m%d")


    DebugLogFile=DEBUG_LOG_PATH+"/%s-%s.log" %(LOG_STRING,strLine)  #/PIT/logs/Debug/iTIS_1.5-DEBUG_LOG-111215.log



    print  DebugLogFile

    global G_DEBUG_File

    if (os.path.isdir(DEBUG_LOG_PATH)!=0):

        G_DEBUG_File=open (DebugLogFile,'a')
    else:

        print "debug log file is not exit"

        return False

    return True

def CloseDebugLog():

    G_DEBUG_File.close()

def StopManualUpdate():

    iStop=15

    nRet=Test_TmccSendCommand(iStop,None,None)



    if (nRet!=0):

        lineno=inspect.getlineno(inspect.currentframe())+2

        WriteDebugLogFile("Send stop command failed",Module_Name,lineno,30)





def ManualUpdate():

    lineno=inspect.getlineno(inspect.currentframe())+2

    WriteDebugLogFile("Enter into the manual updte function",Module_Name,lineno,90)

    iCommand=14 #command:start manual update

    iStop=15    #command:stop manual update

    bSkedUpdate=0

    iRunning=0   #update status

    iUPPercent=0 #update percent

    iUPStatus=0  #update result

    bRet=1

    bNeedReload=False

    bFirst=False

    MAX_EXE_COUNT=20000
    #for recorder the result

    global RunningStatus

    TmccAUStatus=Test_TmccGetUpdateStatus(0)
    #print TmccAUStatus
    iRunning=TmccAUStatus[0]
    #print iRunning
    try:
        if iRunning==2 or iRunning==4:
            bRet=Test_TmccSendCommand(iStop,None,None)

            if bRet==0:

                lineno=inspect.getlineno(inspect.currentframe())+2

                WriteDebugLogFile("The still running update process is stopped now",Module_Name,lineno,90)

            else:

                lineno=inspect.getlineno(inspect.currentframe())+2

                WriteDebugLogFile("The running update process can't be stopped",Module_Name,lineno,30)


        time.sleep(2)
        #print "enter"
        bRet=Test_TmccSendCommand(iCommand,None,None)
        #print bRet
        if bRet<>0:
            #print "enter bRet<>0"

            lineno=inspect.getlineno(inspect.currentframe())+2

            WriteDebugLogFile("The manual update command is sent to the core module unsuccussfully",\
                               Module_Name,lineno,30)

            return False


        iExeNum=0




        while 1:

            time.sleep(1)

            nRet=0

            TmccAUStatus=Test_TmccGetUpdateStatus(0)



            if TmccAUStatus==None:

                lineno=inspect.getlineno(inspect.currentframe())+2
                #print "Calling getupdatestatus function failed"
                WriteDebugLogFile("Calling getupdatestatus function failed",\
                                       Module_Name,lineno,30)

                return False



            iRunning=TmccAUStatus[0]

            RunningStatus=iRunning



            iUPPercent=TmccAUStatus[1]

            iUPStatus=TmccAUStatus[2]


            #print "iRunning:",iRunning
            if iRunning==4 and iUPPercent==100:

                lineno=inspect.getlineno(inspect.currentframe())+2

                WriteDebugLogFile("The manual update is finished successfully",Module_Name,lineno,90)

                GetPatternVersion() ##write the pattern file to get the version info

                break


            elif iRunning==2: #running

                if bFirst==False:

                    lineno=inspect.getlineno(inspect.currentframe())+2

                    WriteDebugLogFile("The manual update is started ",Module_Name,lineno,90)

                    bFirst=True


            elif iRunning==5:

                if bFirst==True:

                    lineno=inspect.getlineno(inspect.currentframe())+2

                    WriteDebugLogFile("The download is finished ",Module_Name,lineno,90)

                    bFirst=False


            elif iRunning==6:###TMCC_TASK_AU_DOWNLOAD_FINISHED

                if bFirst==False:

                    lineno=inspect.getlineno(inspect.currentframe())+2

                    WriteDebugLogFile("The download is finished and need to reload ",Module_Name,lineno,90)

                    bFirst=True

                time.sleep(120)

                bNeedReload=True

                status=Test_TmccGetUpdateStatus()  # miss paramter "0"

                iRunning=status[0]

                iUPPercent=status[1]

                iUPStatus=status[2]

                if iRunning==0 and iUPPercent==0 and iUPStatus==0:

                    lineno=inspect.getlineno(inspect.currentframe())+2

                    WriteDebugLogFile("The update s finished ",Module_Name,lineno,90)

                    break



            elif iRunning==7:

                lineno=inspect.getlineno(inspect.currentframe())+2
                print "The update meets errors, error number:",iUPStatus,Module_Name
                WriteDebugLogFile("The update meets errors, error number:%d " %iUPStatus,\
                                  Module_Name,lineno,30)


                return -1

            iExeNum=iExeNum+1

            if iExeNum>MAX_EXE_COUNT:
                WriteDebugLogFile("iExeNum",iExeNum,lineno,30)
                WriteDebugLogFile("MAX_EXE_COUNT",MAX_EXE_COUNT,lineno,30)

                lineno=inspect.getlineno(inspect.currentframe())+2
                #print "The update is timeout "
                WriteDebugLogFile("The update is timeout ",Module_Name,lineno,30)

                break


        return 0
    except RuntimeError,e:
        print e










def signalManualUpdate(sig,id):

    print "in sigint"

    sys.exit(1)




if __name__ == "__main__":


##    signal.signal(signal.SIGPIPE,signal.SIG_IGN)
    signal.signal(signal.SIGINT,signalManualUpdate)

    iRet=Test_TmccInit()

    print iRet;

    if iRet==0:

        GetDebugLogFile()

        iMRet=ManualUpdate()

        CloseDebugLog()


    try:

        iRet=Test_TmccRelease()


    except:

        print iRet

    print iMRet





