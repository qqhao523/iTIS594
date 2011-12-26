#!/usr/bin/env python
import os
import sys
import Command
import TMSqlite
import time
import signal

TMCCDB = "/Library/Application Support/TrendMicro/common/var/TmccMacLog.db"
CLEANSAVEDIR = "/Library/Application Support/TrendMicro/common/lib/vsapi/cleansave"
QUARANTINEDIR = "/Library/Application Support/TrendMicro/common/lib/vsapi/quarantine"

ScanStatus=-1
bFlag=False
TMCMD_AV_STOP_SCAN = 2

TMFM_AV = 2
def parseStr( strIn ):
        strIn = strIn.replace( " ", "\\ " )
        strIn = strIn.replace( "!", "\\!" )
        #           strIn = strIn.replace( "\\", "\\\\" )
        strIn = strIn.replace( "#", "\\#" )
        strIn = strIn.replace( '"', '\\"' )
        strIn = strIn.replace( "$", "\\$" )
        strIn = strIn.replace( "%", "\\%" )
        strIn = strIn.replace( "&", "\\&" )
        strIn = strIn.replace( "'", "\\'" )
        strIn = strIn.replace( "(", "\\(" )
        strIn = strIn.replace( ")", "\\)" )
        strIn = strIn.replace( "=", "\\=" )
        strIn = strIn.replace( "[", "\\[" )
        strIn = strIn.replace( "]", "\\]" )
        return strIn

def StopManualScan():

        global TMCMD_AV_STOP_SCAN

        global TMFM_AV

        nRet=Command.Test_TmccSendCommand( TMFM_AV, TMCMD_AV_STOP_SCAN )

        return nRet
        
def ScanSignal(sig,id):

##        print ScanStatus;
##
##        if sig==signal.SIGINT:
##                if ScanStatus==2 or ScanStatus==1:
##                        StopManualScan()
        if sig==signal.SIGINT:
                sys.exit(1)
                

signal.signal(signal.SIGINT,ScanSignal)

objTMSqlite = TMSqlite.TMSqlite( )
objTMSqlite.connectDB( TMCCDB )



#print "rm CLEANSAVEDIR", parseStr( CLEANSAVEDIR )
#print "rm QUARANTINEDIR", parseStr( QUARANTINEDIR )
os.system( "sudo rm -rf " + parseStr( CLEANSAVEDIR ) )
os.system( "sudo mkdir " + parseStr( CLEANSAVEDIR ) )
os.system( "sudo rm -rf " + parseStr( QUARANTINEDIR ) )
os.system( "sudo mkdir " + parseStr( QUARANTINEDIR ) )

objTMSqlite.deleteQuarantine( )
objTMSqlite.deleteMalware( )

#signal.signal(signal.SIGINT,ScanSignal)

lstFiles = []
i = 1
iLen = len( sys.argv )
while i < iLen:
#        print os.path.expanduser( sys.argv[i] )
        lstFiles.append( os.path.expanduser( sys.argv[i] ) )
        i += 1
Command.Test_TmccSendCommand( 2, 9 )
time.sleep( 3 )
Command.Test_TmccManualScanStart( lstFiles )

while True:
#        print "sleep 3s"
        lstScanStatus = Command.Test_TmccGetScanStatus( False )

        ScanStatus=lstScanStatus[0]
        time.sleep( 3 )
#        print lstScanStatus
        if lstScanStatus[ 0 ] == 4: #and lstScanStatus[ 1 ] == 100:
                break

iCleanedNum = objTMSqlite.getCleanNum( )
iQuarantineNum = objTMSqlite.getQuarantineNum( )

strRet = "Total:" + str( lstScanStatus[2] ) + ";Scanned:" + str( lstScanStatus[3] ) + ";Malware:" + str( lstScanStatus[4] ) + ";Malware Cleaned:" + str( iCleanedNum ) + ";Malware Quarantined:" + str( iQuarantineNum ) + ";Result:" + str( lstScanStatus[6] )

#lstMalwareLog = objTMSqlite.getMalwareLog( )

#print "VirusName", "\t", "Type", "\t", "File", "\t", "Action", "\t", "Time\n"
#for eachLine in lstMalwareLog:
#        print eachLine[6], "\t", eachLine[4], "\t", eachLine[5], "\t", eachLine[7], "\t", str( time.ctime( eachLine[3] ) )

objTMSqlite.closeDB( )
#Command.Test_TmccSendCommand( 2, 8 )
print strRet
