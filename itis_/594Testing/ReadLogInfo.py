###########Function name:Get log information##########
###########Description: this module is just used to read######
########### the dbfile to get the log information########
########### Author: zhouyanping             ##########
########### Date:   2008-10-6               ##########

##File Name: ReadLogInfo.py
import sqlite3
import time
DBFullName="/Library/Application Support/TrendMicro/Common/var/TmccMacLog.db"
TableName="ZUPDATE"

def ConnectDB(DBName=""):
    connDB=sqlite3.connect(DBFullName)
    if connDB==None:
        print "???? DB connection failure ??????"
    return connDB

def GetUpdateBeforeInformation(connDB):
    
    countList=[]
    cur=connDB.cursor()
    strSQL="select * from ZUPDATE order by Z_PK desc"
    cur.execute(strSQL)
    countList=cur.fetchone()
      
    if countList==None:
        return 0
    else:
        return countList[1]

def GetTheUpdateInformation(connDB,nIndex):
    nRet=0
    strSQL="select * from "+TableName+" where Z_PK>%d"%nIndex
    
    cur=connDB.cursor()
    cur.execute(strSQL)
    countList=cur.fetchall()
   
    if PrintLogInformation(countList)==-1:
        nRet=-1
    
    cur.close()
    
    return len(countList)
def CloseDB(connDB):
    connDB.close()
def PrintLogInformation(countList):
    countlines=len(countList)
    
    if countlines==-1:
        return -1
    print countlines
    for i in range(0,countlines):
        print "Option""  OldVersion""  New version""  component name   "\
              "   Update date   "
        print  countList[i][2],"     ",countList[i][7],"  ",\
              countList[i][6],"    ",countList[i][5],\
            "   ",time.ctime(countList[i][3])
        
    return 0

#GetUpdateBeforeInformation(connDB)

    

    
