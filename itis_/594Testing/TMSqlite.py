import sqlite3 
import os
import time

class TMSqlite( object ): 
        def __init__( self ): 
                self.maxQTDate = 0
                self.maxCNDate = 0
                pass

        def connectDB( self, strDBPath ):
#                print "Connect to DB", strDBPath
                self.cxn = sqlite3.connect( strDBPath )

#                print ".."

                iSize = os.path.getsize( strDBPath )
                if iSize == 0:
                        self.maxQTDate = 0
                        self.maxCNDate = 0
                else:
                        self.maxQTDate = self.getMaxQTDate( )
                        self.maxCNDate = self.getMaxCNDate( )

#                print self.maxQTDate

#                print "Connect Success"

        def getMaxQTDate( self ):
                cur = self.cxn.cursor( )
                cur.execute( "SELECT MAX(ZDATE) FROM ZQUARANTINE" )
                maxQTDate = cur.fetchone( )[ 0 ]
                if maxQTDate == None:
                        maxQTDate = 0
                cur.close( ) 
                return maxQTDate

        def getMaxCNDate( self ):
                cur = self.cxn.cursor( )
                cur.execute( "SELECT MAX(ZDATE) FROM ZMALWARE" )
                maxCNDate = cur.fetchone( )[ 0 ]
                if maxCNDate == None:
                        maxCNDate = 0
                cur.close( ) 
                return maxCNDate

        def getQuarantinedFiles( self ):
                lstQTFile = []
                cur = self.cxn.cursor( )
                cur.execute( "SELECT * FROM ZQUARANTINE WHERE ZDATE>" + str( self.maxQTDate ) )
#                cur.execute( "SELECT * FROM ZQUARANTINE" )
                for eachFile in cur.fetchall( ):
                        print eachFile
                        lstQTFile.append( eachFile[0] )
                cur.close( )

                return lstQTFile
        def deleteQuarantine( self ):
                cur = self.cxn.cursor( )
                cur.execute( "DELETE FROM ZQUARANTINE;" )
                self.cxn.commit( )
                cur.close( )
        
        def deleteMalware( self ):
                cur = self.cxn.cursor( )
                cur.execute( "DELETE FROM ZMALWARE;" )
                self.cxn.commit( )
                cur.close( )
        def getMalwareLog( self ):
                lstMalwareLog = []
                cur = self.cxn.cursor( )
                cur.execute( "SELECT * FROM ZMALWARE;" )
                for eachFile in cur.fetchall( ):
                        lstMalwareLog.append( eachFile )
                cur.close( )
                return lstMalwareLog

        def getCleanedFiles( self ):
                lstCNFile = []
                cur = self.cxn.cursor( )
                cur.execute( "SELECT ZFILE FROM ZMALWARE WHERE ZACTION='cleaned'" )

                for eachFile in cur.fetchall( ):
                        lstCNFile.append( eachFile )
                        print eachFile

#                cur.execute( "SELECT * FROM ZMALWARE" )
#                for eachItem in cur.fetchall( ):
#                        print eachItem
                cur.close( )

                return lstCNFile
        def getCleanNum( self ):
                cur = self.cxn.cursor( )
                cur.execute( "Select count(*) from zmalware where zaction='cleaned'" )
                iRet = int( cur.fetchall( )[0][0] )
#                print cur.fetchall()
                cur.close( )
                return iRet

        def getQuarantineNum( self ):
                cur = self.cxn.cursor( )
                cur.execute( "Select count(*) from zquarantine" )
                iRet = int( cur.fetchall( )[0][0] )
#                print cur.fetchall()
                cur.close( )
                return iRet
        def closeDB( self ):
                self.cxn.close( )
                


#        def isQuarantined( self, strName ):
#                self.c


#objTMSqlite = TMSqlite( )
#objTMSqlite.connectDB( "/Library/Application Support/TrendMicro/common/var/TmccMacLog.db" )
#time.sleep( 3 )
#objTMSqlite.deleteQuarantine( )
#print objTMSqlite.getMalwareLog( )

#print "QT"
#ElstQTFile = objTMSqlite.getQuarantinedFiles( )
#for eachItem in lstQTFile:
#        print eachItem
#print "CN"
#lstCNFile = objTMSqlite.getCleanedFiles( )
#for eachItem in lstCNFile:
#        print eachItem
#print objTMSqlite.getCleanNum( )
#objTMSqlite.closeDB( )

