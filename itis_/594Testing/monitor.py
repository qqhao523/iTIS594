#!/usr/bin/env python
import os
import re
import time
import sys
import signal
import commands

iInterval = 5

Memory_UIMgmt = 20
Memory_TmccMainService = 150
Memory_TmccForMac = 20
Memory_TmLogMgr = 10

LogPath = "./log.txt"



        






def GetCPUUsage():

        #strTop=getTop()
    total=0
    times=5

    Str=commands.getoutput('iostat -c 5 -n cpu')
    lines=Str.split('\n')

    for i in range(2,times+1):
        user=lines[i][0:3]
        sys=lines[i][3:6]
        total=total+float(user)+float(sys)	
        
    return total/times
		
        #return 100-getIdleCPU(strTop)

        
    
        

def getPS( ):
        fu = os.popen( "ps -avx | grep iCoreService" )
        strPS = fu.readline( ).split( "\n" )[0]
        fu.close( )

        lstPS = re.split( '\ +', strPS )
        return lstPS
#lstPS = strPS.split( "\t" )

def getTop( ):
        fu = os.popen( "top -l 2 " )
        strTop = fu.read( )
        
        return strTop

def getIdleCPU( strTop ):

        strLine2=strTop.split("\n")

        nCount=len(strLine2)


        i=0

        while 1:
               
                ret=re.match("^\s*$",strLine2[i])
                if ret!=None:
                        
                        strLine2.remove(strLine2[i])
                        nCount=nCount-1
                        
                
                if i==nCount-2:
                        break
                i=i+1
              

        nIndex=(int)(nCount/2)+1

        strTemp=strLine2[nIndex].split(":")

        
        
        if (len(strTemp)<3):
                return 0

        strCPU=strTemp[2]

        

        strTemp=strCPU.split(",");

        if (len(strTemp)<3):

                return 0
        strIdle = strCPU.split( "," )[2]

        strIdlePercent = strIdle.split( "%" )[0]


        iIdlePercent = float( strIdlePercent )


        return iIdlePercent
       

def getProcessRS( strProcessName, strTop ):
        fu = os.popen( "ps -avx | grep '" + strProcessName + "' | grep -v grep" )
        strPS = fu.readline( )
        if len( strPS ) < 2:
                return []
        
        strPS = re.split( '^\ +', strPS )[-1]
        lstPS = re.split( '\ +', strPS )
        iPID = int( lstPS[0] )
        iCPU = float( lstPS[10] )

        lstLine = strTop.split( "\n" )
        lstRS = []

        lstRS.append( iCPU )
        iNum = 0
        for eachLine in lstLine:
                eachLine = re.split( '^\ +', eachLine )[-1]
                lstTmp = eachLine.split( '%' )
                
                if iNum < 9:
                        iNum += 1
                        continue

                if len( lstTmp ) < 2:
                        continue

                lstBeforeCPU = re.split( '\ +', lstTmp[0] )
                strTmp = re.split( '^\ +', lstTmp[1] )[-1]
                lstAfterCPU = re.split( '\ +', strTmp )

                if int( lstBeforeCPU[0] ) == iPID:
                        strRMem = lstAfterCPU[-2]
                        strVMem = lstAfterCPU[-1]
                        
                        iRMem = int( strRMem[:-2] )
                        if strRMem[-2] == "M":
                                iRMem = 1024 * iRMem
                        
                        iVMem = int( strVMem[:-2] )
                        if strVMem[-2] == "M":
                                iVMem = 1024 * iVMem

#                        print "iVMem", iVMem
                        lstRS.append( iRMem )
                        lstRS.append( iVMem )

                        lstRS.append( int( lstAfterCPU[1] ) )
                        
                        break
                else:
                        continue
#        print lstRS
        return lstRS

def checkCrash( ):
        fu = os.popen( "ls /Library/Logs/CrashReporter/ | grep -E '(UIMgmt|Tmcc|Trend|TmLogin)'" )
        strLS = fu.read( )
        if len( strLS ) != 0:
                return True
        fu = os.popen( "ls ~/Library/Logs/CrashReporter/ | grep -E '(UIMgmt|Tmcc|Trend|TmLogin)'" )
        strLS = fu.read( )
        if len( strLS ) != 0:
                return True
        return False

def checkHang( ):
        fu = os.popen( "ls /Library/Logs/HangReporter/Trend\ Micro\ Common\ Client\ for\ Mac | grep -E '(UIMgmt|Tmcc|Trend|TmLogin)'" )
        strLS = fu.read( )
        if len( strLS ) != 0:
                return True
        return False



def writeLog( strLog ):
        fd = open( LogPath, "a" )
        fd.write( strLog + "_" + str( time.ctime( ) ) + "\n" )
        fd.close( )

#checkCrash( )
##iNumFullCPU = 0
##iLastIdleCPU = 100
##
##writeLog( "test1" )
##writeLog( "test2" )
##
##
##while True:
##        strTop = getTop( )
##        iIdleCPU = getIdleCPU( strTop )
##        print "IdleCPU\t\t\t", iIdleCPU
##        if iIdleCPU == 0:
##                iNumFullCPU += 1
##        else:
##                iNumFullCPU = 0
##        if iNumFullCPU >= 30 / iInterval:
##                writeLog( "Full CPU more than 30 seconds" )
##                print "Fail_HighCPU"
###                break
##
##        lstProcessRS =  getProcessRS( "TmccMainService", strTop )
##        print "TmccMainService\t\t", lstProcessRS
##        if len( lstProcessRS ) == 0:
##                writeLog( "TmccMainService Process Disapear"  )
###                print "Fail_TmccMainService_Disappear"
###                break
##        if lstProcessRS[1] > Memory_TmccMainService * 1024:
##                writeLog( "TmccMainService Memory Leak" + str( lstProcessRS[1] ) )
##                print "Fail_MemoryLeak_TmccMainService"
##                break
##        if lstProcessRS[3] > 40:
##                writeLog( "TmccMainService Thread Leak " + str( lstProcessRS[3] ) )
##                print "Fail_Thread_Leadk"
##                break
##
##
##        lstProcessRS1 = getProcessRS( "UIMgmt", strTop )
##        print "UIMgmt\t\t\t", lstProcessRS1
##        if len( lstProcessRS1 ) == 0:
##                writeLog( "UIMgmt Process Disapear"  )
##                print "Fail_UIMgmt_Disappear"
###                break
##        if lstProcessRS1[1] > Memory_UIMgmt * 1024:
##                writeLog( "UIMgmt Memory Leak " + str( lstProcessRS1[1] ) )
##                print "Fail_MemoryLeak_UIMgmt"
###                break
##
##        lstProcessRS2 = getProcessRS( "Trend Micro Common Client for Mac", strTop )
##        print "TMCC for Mac\t\t", lstProcessRS2
##        if len( lstProcessRS2 ) == 3:
##                if lstProcessRS2[1] > Memory_TmccForMac * 1024:
##                        writeLog( "TMCC For Mac Memory Leak " + str( lstProcessRS2[1] ) )
##                        print "Fail_MemoryLeak_Trend Micro Common Client for Mac"
###                        break
##
##        lstProcessRS3 = getProcessRS( "TmLoginMgr", strTop )
##        print "TmLoginMgr\t\t", lstProcessRS3
##        print "\n"
##        if len( lstProcessRS3 ) == 0:
##                writeLog( "TmLoginMgr Process Disapear"  )
##                print "Fail_TmLoginMgr_Disappear"
###                break
##        if lstProcessRS3[1] > Memory_TmLogMgr * 1024:
##                writeLog( "TmloginMgr Memory Leak " + str( lstProcessRS3[1] ) )
##                print "Fail_MemoryLeak_TmloginMgr"
###                break
##
##        if checkCrash( ):
##                writeLog( "Crash" )
##                print "Fail_Crash"
###                break
##
##        if checkHang( ):
##                writeLog( "Hang" )
##                print "Fail_Hang"
###                break
##        
##
##
##        
##        time.sleep( iInterval )

#lstPS = getPS( )

#pCPU = lstPS[11]
#pMem = lstPS[12]
#print "CPU: ", pCPU
#print "pMem: ", pMem
def signalHandle(sig,id):

        if sig==signal.SIGQUIT or sig==signal.SIGINT:

                lines=logf.readlines()

                iIndex=len(lines)-1

              
                if (iIndex>0):

                        lines.remove(lines[iIndex])

                        lines.writelines(lines)
                
                logf.close()

                sys.exit(1)
                
  

                



if __name__=="__main__":

        ilen=len(sys.argv);
        print ilen
        LoopTime=1
        
        if ilen>=2 and sys.argv[1]<>"":
                strLogName=sys.argv[1]
                
        if ilen>=3 and sys.argv[2]<>"":
                LoopTime=sys.argv[2]
                print "LoopTime=",LoopTime

        logf=open(strLogName,'a+')

        signal.signal(signal.SIGQUIT,signalHandle)

        signal.signal(signal.SIGINT,signalHandle)

        icount=0

        time.sleep(1)

        while 1:
                
                time.sleep(float(LoopTime-1))

              
                cpuusage=GetCPUUsage()
        

                strCPU=str(cpuusage)

                strLine=time.strftime("[%Y/%m/%d %T]")
                

                strLine1=("%s\t%s\n" %(strLine,strCPU))

                logf.write(strLine1)

               
            

       
