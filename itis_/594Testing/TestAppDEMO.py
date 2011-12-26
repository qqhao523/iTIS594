#!/usr/bin/env python
#test for c header file transfer to python
#TestApp.py

from ctypes import *

import os, sys, time

#test = cdll.LoadLibrary('/Library/Application Support/TrendMicro/common/lib/libTmccMacClientLib.dylib')
LIBRARYPATH = "/Library/Frameworks/iCoreClient.framework/Versions/A/iCoreClient"

test=cdll.LoadLibrary(LIBRARYPATH)
if test==None:
    print "error"

TMCC_COMP_NUMBER=6



########################################################
######             Define Content            ###########
########################################################

TMCC_MAC_MAX_HOSTNAME_LEN = 127
TMCC_MAC_MAX_URL_LEN = 2047
TMCC_MAC_MAX_ADDR_LEN = 48
TMCC_MAC_MAX_USERNAME_LEN = 63
TMCC_MAC_MAX_PASSWORD_LEN = 63
TMCC_MAC_MAX_PATH_LEN = 2047
TMCC_MAC_MAX_FILENAME_LEN = 255
TMCC_MAC_MAX_MALWARE_LEN = 255
TMCC_MAC_MAX_CMD_RES_LEN = 255
TMCC_MAC_MAX_VER_LEN = 127
TMCC_MAC_MAX_CMD_RESULT_LEN = 127
iCORE_MAX_UPDATE_COMPONENT_LISTSIZE=		16
TMCC_PX_WEB_PROTECT_MAX_LIST_RECORD = 500
TMCC_PX_WEB_PROTECT_MAX_CATEGORY_NAME_LENGTH = 127

TMCC_PX_WEB_PROTECT_MAX_CATEGORY = 128
TMCC_PX_WEB_PROTECT_WTP_THREAT_STRLEN = 64

#######################################################
#######     init and release               ############
#######################################################
def Test_TmccInit():
   
    return Test.TmccInit()

def Test_TmccRelease():
  
    nRet=test.TmccRelease()
    try:
        print nRet
    except:
        print "release error"
    return nRet

########################################################
######             RT & Manual Scan          ###########
########################################################


class Schd_StartDay(Union):
    _fields_=[("Mday",c_int),
              ("Wday",c_int)]

class Test_Schedule_t(Structure):
    _fields_=[("RepeatInterval",c_int),
              ("StarDay",Schd_StartDay),
             ("StarTime",c_int),
              ("IntervalHours",c_int)]
##class Test_Schedule_t(Structure):
##    _fields_=[("RepeatInterval",c_int),
##              ("StarDay",c_int),
##              ("StartTime",c_int)]
class Test_String_t(Structure):
    _fields_=[("wszString",c_char_p),
              ("lenth",c_int)]

test_String_P = POINTER(Test_String_t)

class Test_ScanTarget_T(Structure):
    _fields_=[("ScanTargetType",c_int),
              ("Filcount",c_int),
              ("FileList",test_String_P)]

class Test_ScanAction_T(Structure):
    _fields_=[("ScanCategory",c_int),
              ("firstAction",c_int),
              ("secondAction",c_int)]

class Test_ScanOption_T(Structure):
    _fields_=[("bScanCompressed",c_int),
              ("Action",Test_ScanAction_T)]
    


def Test_TmccSetRTScanOptions( bScanInsertsk, bScanCompressed, iScanCategory, iFirstAction, iSecondAction ):
    test_ScanOption_T = Test_ScanOption_T()
    
    test_ScanOption_T.bScanCompressed = bScanCompressed
    test_ScanOption_T.Action.ScanCategory = iScanCategory
    test_ScanOption_T.Action.firstAction = iFirstAction
    test_ScanOption_T.Action.secondAction = iSecondAction
    
    test.TmccSetRTScanOptions(bScanInsertDisk, test_ScanOption_T)


def Test_TmccGetRTScanOptions():
    test_ScanOption_T = Test_ScanOption_T()
    bScanI = c_int()
    test.TmccGetRTScanOptions(pointer(bScanI), pointer(test_ScanOption_T))

    bScanInsertDisk = bScanI.value
    bScanCompressed = test_ScanOption_T.bScanCompressed 
    iScanCategory = test_ScanOption_T.Action.ScanCategory
    iFirstAction = test_ScanOption_T.Action.firstAction
    iSecondAction = test_ScanOption_T.Action.secondAction

    RTSList = [bScanInsertDisk,bScanCompressed,iScanCategory,iFirstAction,iSecondAction]
    return RTSList
    

def Test_TmccSetManualScanOptions( iScanTargetType, iFileCount, lstFileList, bScanCompressed, iScanCategory, iFirstAction, iSecondAction ):
    test_ScanTarget_T = Test_ScanTarget_T()
    test_ScanOption_T = Test_ScanOption_T()

    array = Test_String_t * len(lstFileList)
    T_String = array()
    
    test_ScanTarget_T.ScanTargetType = iScanTargetType
    test_ScanTarget_T.Filcount = len(lstFileList)
    
    i = 0
    while i < len(lstFileList):
        T_String[i] = Test_String_t()
        T_String[i].wszString = lstFileList[i]
        T_String[i].lenth = len(lstFileList[i])
        i += 1

    test_ScanTarget_T.FileList = cast(point(T_String),POINTER(Test_String_t))
    
    test_ScanOption_T.bScanCompressed = bScanCompressed
    test_ScanOption_T.Action.ScanCategory = iScanCategory
    test_ScanOption_T.Action.firstAction = iFirstAction
    test_ScanOption_T.Action.secondAction = iSecondAction    

    test.TmccSetManualScanOptions(pointer(test_ScanTarget_T), test_ScanOption_T)


def Test_TmccGetManualScanOptionsCreate():
    test_ScanTarget_T = Test_ScanTarget_T()
    test_ScanOption_T = Test_ScanOption_T()
    test.TmccGetManualScanOptionsCreate(pointer(test_ScanTarget_T), pointer(test_ScanOption_T))

    iScanTargetType = test_ScanTarget_T.ScanTargetType
    iFileCount = test_ScanTarget_T.Filcount

    lstFileList = []   
    i = 0
    while i < iFileCount:
        
        lstFileList[i].append(test_ScanTarget_T.FileList[i].wszString)
        i += 1

       

    bScanCompressed = test_ScanOption_T.bScanCompressed 
    iScanCategory = test_ScanOption_T.Action.ScanCategory
    iFirstAction = test_ScanOption_T.Action.firstAction
    iSecondAction = test_ScanOption_T.Action.secondAction

    Target = [iScanTargetType,iFileCount,lstFileList]
    Option = [bScanCompressed,iScanCategory,iFirstAction,iSecondAction]
    return Target,Option

def Test_TmccGetManualScanOptionsRelease():
    test_ScanTarget_T = Test_ScanTarget_T()
    test_ScanOption_T = Test_ScanOption_T()
    test.TmccGetManualScanOptions(pointer(test_ScanTarget_T), pointer(test_ScanOption_T))





########################################################
######              Schedule Scan            ###########
########################################################

    

def Test_TmccSetSchdScanOptions(iScanTargetType, iFileCount, lstFileList, bScanCompressed, iScanCategory, iFirstAction, iSecondAction, iRepeatInterval,iStartday,iStartTime):
    test_ScanTarget_T = Test_ScanTarget_T()
    test_ScanOption_T = Test_ScanOption_T()
    test_Schedule_T = Test_Schedule_t()

    array = Test_String_t * len(lstFileList)
    T_String = array()
    
    test_ScanTarget_T.ScanTargetType = iscanTargetType
    test_ScanTarget_T.Filcount = len(lstFileList)
    
    i = 0
    while i < len(lstFileList):
        T_String[i] = Test_String_t()
        T_String[i].wszString = lstFileList[i]
        T_String[i].lenth = len(lstFileList[i])
        i += 1

    test_ScanTarget_T.FileList = cast(point(T_String),POINTER(Test_String_t))
    
    test_ScanOption_T.bScanCompressed = bscanCompressed
    test_ScanOption_T.Action.ScanCategory = iScanCategory
    test_ScanOption_T.Action.firstAction = iFirstAction
    test_ScanOption_T.Action.secondAction = iSecondAction

    test_Schedule_T.RepeatInterval = iRepeatInterval

    if iRepeatInterval == 3:
        test_Schedule_T.StarDay.Wday=iStartDay
        test_Schedule_T.StarDay.Mday=0
    elif iRepeatInterval == 4:
        test_Schedule_T.StarDay.Mday=iStartDay
        test_Schedule_T.StarDay.Wday=0
    else:
        test_Schedule_T.StarDay.Wday = 0
        test_Schedule_T.StarDay.Mday = 0
        
    
    test_Schedule_T.StarTime = iStartTime

    test.TmccSetManualScanOptions(test_ScanTarget_T, test_ScanOption_T,test_Schedule_T)


def Test_TmccGetScheduleScanOptionsCreate():
    test_ScanTarget_T = Test_ScanTarget_T()
    test_ScanOption_T = Test_ScanOption_T()
    test_Schedule_T = Test_Schedule_t()
    test.TmccGetManualScanOptionsCreate(pointer(test_ScanTarget_T), pointer(test_ScanOption_T),pointer(test_Schedule_T))

    iScanTargetType = test_ScanTarget_T.ScanTargetType
    iFileCount = test_ScanTarget_T.Filcount

    lstFileList = []   
    i = 0
    while i < iFileCount:
        
        lstFileList[i].append(test_ScanTarget_T.FileList[i].wszString)
        i += 1

    bScanCompressed = test_ScanOption_T.bScanCompressed 
    iScanCategory = test_ScanOption_T.Action.ScanCategory
    iFirstAction = test_ScanOption_T.Action.firstAction
    iSecondAction = test_ScanOption_T.Action.secondAction

    iRepeatInterval = test_Schedule_T.RepeatInterval

    if iRepeatInterval == 3:
        iStartDay = test_Schedule_T.StarDay.Wday

    elif iRepeatInterval == 4:
         iStartDay = test_Schedule_T.StarDay.Mday
       
    else:
        iStartDay = 0

    iStartTime = test_Schedule_T.StarTime

    Target = [iScanTargetType,iFileCount,lstFileList]
    Option = [bScanCompressed,iScanCategory,iFirstAction,iSecondAction]
    Schedule = [iRepeatInterval, iStartDay,iStartTime]
    return Target,Option,Schedule
    


def Test_TmccGetScheduleScanOptionsRelease():
    test_ScanTarget_T = Test_ScanTarget_T()
    test_ScanOption_T = Test_ScanOption_T()
    test_Schedule_T = Test_Schedule_t()
    test.TmccGetManualScanOptionsRelease(pointer(test_ScanTarget_T), pointer(test_ScanOption_T),pointer(test_Schedule_T))


########################################################
######             Operation                 ###########
########################################################

class Test_TmccScanStatus_t(Structure):
    _fields_=[("bRunning",c_int),
              ("ScanPercent",c_int),
              ("TotalNum",c_int),
              ("ScanedNum",c_int),
              ("ThreatNum",c_int),
              ("ScanFileName",c_char*(TMCC_MAC_MAX_PATH_LEN+1))]
                                  


def Test_ManualScanStart(iScanTargetType, iFileCount, lstFileList, bScanCompressed, iScanCategory, iFirstAction, iSecondAction ):
    test_ScanTarget_T = Test_ScanTarget_T()
    

    array = Test_String_t * len(lstFileList)
    T_String = array()
    
    test_ScanTarget_T.ScanTargetType = iscanTargetType
    test_ScanTarget_T.Filcount = len(lstFileList)
    
    i = 0
    while i < len(lstFileList):
        T_String[i] = Test_String_t()
        T_String[i].wszString = lstFileList[i]
        T_String[i].lenth = len(lstFileList[i])
        i += 1

    test_ScanTarget_T.FileList = cast(point(T_String),POINTER(Test_String_t))
    
    test.TmccSetManualScanOptions(pointer(test_ScanTarget_T))


def Test_TmccGetScanStatus(bSchedScan):
    test_TmccScanStatus_t = Test_TmccScanStatus_t()

    test.TmccGetScanStatus(bSchedScan, pointer(test_TmccScanStatus_t))

    iRunning = test_TmccScanStatus_t.bRunning
    iScanPercent = test_TmccScanStatus_t.ScanPercent
    iTotalNum = test_TmccScanStatus_t.TotalNum
    iScanedNum = test_TmccScanStatus_t.ScanedNum
    iThreatNum = test_TmccScanStatus_t.ThreatNum
    strScanFileName = test_TmccScanStatus_t.ScanFileName
    lstRet = [iRunning,iScanPercent,iTotalNum,iScanedNum,iThreatNum,strScanFileName]
    return lstRet



def Test_TmccQuarantineFileOperation(Qitem,Qaction):
    test.TmccQuarantineFileOperation(Qitem,Qaction)



class Test_TmccCommandResu_t(Structure):
    _fields_=[("resValue",c_int),
              ("resData",c_char*(TMCC_MAC_MAX_CMD_RESULT_LEN+1))]


def Test_TmccSendCommand(iCommand, lPamrm=None, pResult=None):

    if not lPamrm == None:
        lPamrm = None

    if not pResult == None:
        pResult = None
    test_TmccCommandResu_t = Test_TmccCommandResu_t()

    RET=test.TmccSendCommand( iCommand, None, None)
    print "Ret=",RET,"in TmccSendCommand"
    return RET
                                         


########################################################
######             Exception                 ###########
########################################################


def Test_TmccSetScanExceptionList(ExFileCount, lstExFileList,ExFileExtCount,lstExFileExtList):
    arrayFile = Test_String_t * len(lstExFileList)
    T_Exp_File = arrayFile()
    arrayFileExt = Test_String_t * len(lstExFileExtList)
    T_Exp_FileExt = arrayFileExt()

    i=0
    while i<len(lstExFileList):
        T_Exp_File[i] = Test_String_t()
        T_Exp_File[i].wszString = lstExFileList[i]
        T_Exp_File[i].lenth = len(lstExFileList[i])
        
        i = i+1

        
    j=0
    
    while j<len(lstExFileList):
        T_Exp_FileExt[i] = Test_String_t()
        T_Exp_FileExt[i].wszString = lstExFileExtList[i]
        T_Exp_FileExt[i].lenth = len(lstExFileExtList[i])
        
        j =j+1
                                  
    test.Test_TmccSetScanExceptionList(pointer(T_Exp_File),len(lstExFileList),pointer(T_Exp_FileExt),len(lstExFileList))


def Test_TmccGetScanExceptionListCreate():
    T_Exp_File = Test_String_t()
    T_Exp_FileExt = Test_String_t()
    FileCount = c_int()
    FileExtCount = c_int
                                  
    test.Test_TmccGetScanExceptionListCreate(pointer(T_Exp_File),pointer(FileCount),pointer(T_Exp_FileExt),pointer(FileExtCount))

    ExFileCount = FileCount.value
    ExFileExtCount = FileExtCount.value

    lstExFileList = []
    i = 0
    while i < ExFileCount:
        lstExFileList[i].append(T_Exp_File.wszString)
        i += 1

    lstExFileExtList = []
    j = 0
    while j < ExFileExtCount:
        lstExFileExtList[j].append(T_Exp_FileExt.wszString)
        j += 1
    
    return len(lstExFileList),lstExFileList,len(lstExFileExtList),lstExFileExtList

def Test_TmccGetScanExceptionListRelease():
    T_Exp_File = Test_String_t()
    T_Exp_FileExt = Test_String_t()
    FileCount = c_int()
    FileExtCount = c_int
                                  
    test.Test_TmccGetScanExceptionListRelease(pointer(T_Exp_File),pointer(FileCount),pointer(T_Exp_FileExt),pointer(FileExtCount))

                                  

########################################################
######                 AU                    ###########
########################################################

class Test_TmccUpdateStatus_t(Structure):
    _fields_=[("bRunning",c_int),
              ("UpdatePercent",c_int),
              ("UpdateStatus",c_int)]

def Test_TmccSetUpdateSetting(bNeedAutoUpdate, iRepeatInterval, iStartDay,iStartTime,intervalHour):
    test_Schedule_T = Test_Schedule_t()                        
    test_Schedule_T.RepeatInterval = iRepeatInterval
    print "in TmccSetUpdateSetting,iRepeatInterval=",iRepeatInterval,"\n"
   # test_Schedule_T.StarDay=iStartDay
    
    if iRepeatInterval == 3:
        test_Schedule_T.StarDay.Wday=iStartDay
        #test_Schedule_T.StarDay.Mday=0
        print "iStartDay=\n",iStartDay
        
        print "iStartDay in if =",test_Schedule_T.StarDay.Wday,"in setupdatesetting"
    elif iRepeatInterval == 4:
        test_Schedule_T.StarDay.Mday=iStartDay
        #test_Schedule_T.StarDay.Wday=0
    else:
        iStartDay=0
    
    if iRepeatInterval == 5:

        test_Schedule_T.IntervalHours = intervalHour
    else:
        test_Schedule_T.IntervalHours = 0
        
    test_Schedule_T.StarTime = iStartTime

    
      
    nRet=test.TmccSetUpdateSetting(bNeedAutoUpdate,test_Schedule_T)
    print "nRet=",nRet
    return nRet


def Test_TmccGetUpdateSetting():
    test_Schedule_T = Test_Schedule_t()

    iNeedAutoUpdate = c_int()
 
    test.TmccGetUpdateSetting(pointer(iNeedAutoUpdate),pointer(test_Schedule_T))

    bNeedAutoUpdate = iNeedAutoUpdate.value

    iRepeatInterval = test_Schedule_T.RepeatInterval
    
    ##iStartDay=test_Schedule_T.StarDay
    if iRepeatInterval == 3:
        iStartDay = test_Schedule_T.StarDay.Wday
        print "in getupdate setting iStartDay=",iStartDay
    elif iRepeatInterval == 4:
         iStartDay = test_Schedule_T.StarDay.Mday
       
    else:
        iStartDay = 0

    if iRepeatInterval==5:
        intervalHour=test_Schedule_T.IntervalHours
    else:
        intervalHour=0
        
    print "in getupdatesetting, iRepeatInterval=",iRepeatInterval
    iStartTime = test_Schedule_T.StarTime

    ScheduleAU = [bNeedAutoUpdate, iRepeatInterval, iStartDay,iStartTime,intervalHour]
    return ScheduleAU
    
    
def Test_TmccGetUpdateStatus(bSchdUpdate):
    test_TmccUpdateStatus_t = Test_TmccUpdateStatus_t()
    nRet=test.TmccGetUpdateStatus(bSchdUpdate, pointer(test_TmccUpdateStatus_t))
    
    iRunning = test_TmccUpdateStatus_t.bRunning
    iUpdatePercent = test_TmccUpdateStatus_t.UpdatePercent
    iUpdateStatus = test_TmccUpdateStatus_t.UpdateStatus
    
    AUStatus = [iRunning, iUpdatePercent, iUpdateStatus]

    return AUStatus



##########################################################
########                 WTP                   ###########
##########################################################


class Test_TmccProxySetting_t(Structure):
    _fields_=[("bUseProxy",c_int),
              ("Protocol",c_int),
              ("ServerAddress", c_char*(TMCC_MAC_MAX_HOSTNAME_LEN+1)),
              ("Port",c_int),
              ("bNeedPWD",c_int),
              ("UserName",c_char*(TMCC_MAC_MAX_USERNAME_LEN+1)),
              ("Password",c_char*(TMCC_MAC_MAX_PASSWORD_LEN+1))]

class Test_PxWpRecord(Structure):
    _fields_=[("szURL",c_char*(TMCC_MAC_MAX_URL_LEN+1))]

class Test_TmccPxWTPSet_C(Structure):
    _fields_=[("EnableWtp",c_int),
              ("wtpLevel",c_int),
              ("EnableWtpNotify",c_int)]

class Test_PxWpCategorylist(Structure):
    _fields_=[("num",c_int),
              ("Categories",c_int*(TMCC_PX_WEB_PROTECT_MAX_CATEGORY))]

class Test_PxWpCategory_C(Structure):
    _fields_=[("EnableCategoryChk",c_int),
              ("blockCateList",Test_PxWpCategorylist),
              ("EnableCatNotify",c_int)]    

class Test_PxWpCategory(Structure):
    _fields_=[("Category_Code",c_int)] 
  
class Test_PxWpCategory_Group(Structure):
    _fields_=[("Category_GroupCode",c_int),
              ("Category_List",Test_PxWpCategorylist)] 


def Test_TmccSetProxySetting(PxyType, bUseSysPxy, bUsePxy, Proto, Server, Port, bNeedPWD, Username, Password):
    
    test_TmccProxySetting_t = Test_TmccProxySetting_t()

    test_TmccProxySetting_t.bUseProxy = bUsePxy
    if bUsePxy ==1:
        test_TmccProxySetting_t.Protocol = Proto
        test_TmccProxySetting_t.ServerAddress = Server
        test_TmccProxySetting_t.Port = Port
    else:
        test_TmccProxySetting_t.Protocol = 0
        test_TmccProxySetting_t.ServerAddress = ""
        test_TmccProxySetting_t.Port = 0
        
    test_TmccProxySetting_t.bNeedPWD = bNeedPWD
    if bNeedPWD == 1:
        test_TmccProxySetting_t.UserName = Username
        test_TmccProxySetting_t.Password = Password
    else:
        test_TmccProxySetting_t.UserName = ""
        test_TmccProxySetting_t.Password = ""

    test.TmccSetProxySetting(PxyType, bUseSysPxy, test_TmccProxySetting_t)

def Test_TmccGetProxySetting(PxyType):
    test_TmccProxySetting_t = Test_TmccProxySetting_t()

    bUseSysP = c_int()

    test.TmccGetProxySetting(PxyType,pointer(bUseSysP),pointer(test_TmccProxySetting_t))

    bUseSysP = bUseSysP.value

    bUsePxy = test_TmccProxySetting_t.bUseProxy
    if bUsePxy ==1:
        Proto = test_TmccProxySetting_t.Protocol
        Server = test_TmccProxySetting_t.ServerAddress
        Port = test_TmccProxySetting_t.Port
    else:
        Proto = 0
        Server = None
        Port = 0
        
    bNeedPWD = test_TmccProxySetting_t.bNeedPWD

    if bNeedPWD == 1:
        Username = test_TmccProxySetting_t.UserName
        Password = test_TmccProxySetting_t.Password
    else:
        Username = None
        Password = None

    return bUsePxy, bUsePxy, Proto, Server, Port, bNeedPWD, Username, Password
                                  

def Test_TmccPxWpEnable(bEnable,scanType):
    test.TmccPxWpEnable(bEnable,scanType)


def Test_TmccPxWpIsEnabled(scanType):
    iEnabled = c_int()
    test.TmccPxWpIsEnabled(pointer(iEnabled),pointer(scanType))

    return iEnabled



def Test_TmccPxWTPSetConfig(EnableWtp,wtpLevel,EnableWtpNotify):
    test_TmccPxWTPSet_C = Test_TmccPxWTPSet_C()
    test_TmccPxWTPSet_C.EnableWtp = EnableWtp
    test_TmccPxWTPSet_C.wtpLevel = wtpLevel
    test_TmccPxWTPSet_C.EnableWtpNotify = EnableWtpNotify
    
    test.TmccPxWpWTPSetConfig(pointer(test_TmccPxWTPSet_C))

def Test_TmccPxWTPGetConfig():
    test_TmccPxWTPGet_C = Test_TmccPxWTPSet_C()
    test.TmccPxWpWTPGetConfig(pointer(test_TmccPxWTPGet_C))
    EnableWtp = test_TmccPxWTPSet_C.EnableWtp
    wtpLevel = test_TmccPxWTPSet_C.wtpLevel 
    EnableWtpNotify = test_TmccPxWTPSet_C.EnableWtpNotify

    PxWTPGetConfig = [EnableWtp,wtpLevel,EnableWtpNotify]

    return PxWTPGetConfig

  
def Test_TmccPxCatSetConfig(EnableCat,BlockCat,BlockCatNum,EnableCatNotify):
    test_PxWpCategory_C = Test_PxWpCategory_C()

    test_PxWpCategory_C.EnableCategoryChk = EnableCat
    test_PxWpCategory_C.blockCateList.num = BlockCatNum
    test_PxWpCategory_C.EnableCatNotify = EnableCatNotify

    i = 0
    while i < len(BlockCat):
        test_PxWpCategory_C.blockCateList.Categories[i] = BlockCat[i]
        i += 1

    test.TmccPxWpCatSetConfig(pointer(test_PxWpCategory_C))    

def Test_TmccPxCatGetConfig():
    test_PxWpCatGet_C = Test_PxWpCategory_C()
    test.TmccPxWpCatGetConfig(pointer(test_PxWpCatGet_C))

    EnableCat = test_PxWpCategory_C.EnableCategoryChk
    BlockCatNum = test_PxWpCategory_C.blockCateList.num
    EnableCatNotify = test_PxWpCategory_C.EnableCatNotify
    
    i = 0
    BlockCat = []
    while i < BlockCatNum:
        BlockCat[i].append(test_PxWpCategory_C.blockCateList[i].Categories)
        i +=1

    return EnableCat, BlockCatNum, BlockCat, EnableCatNotify


def Test_TmccPxWpExceptEnable(bEnable,listType):
    test.TmccPxWpExceptEnable(bEnable,listType)


def Test_TmccPxWpExceptIsEnable():
    Enable = c_int()
    Type = c_int()
    test.TmccPxWpExceptIsEnable(pointer(Enable),Type)

    bEnable = Enable.value

    if bEnable == 1:
        ListType = Type
    else:
        ListType = None

    return bEnable, ListType


def Test_TmccPxSetRecordList(listType,TmccPxWpRecordList,count):
    Array=Test_PxWpRecord*len(TmccPxWpRecordList)
    test_PxWpRecord = Array()

    i = 0
    while i < len(TmccPxWpRecordList):
        test_PxWpRecord[i] = Test_PxWpRecord()
        test_PxWpRecord[i].szURL = TmccPxWpRecordList[i]
        i = i+1
    
    test.TmccPxSetRecordList(listType,pointer(test_PxWpRecord),count)

def Test_TmccPxGetRecordList(listType):
    test_TmccPxGetRecordList = Test_PxWpRecord()
    Count = c_int()
    test.TmccPxGetRecordList(listType, pointer(test_TmccPxGetRecordList), pointer(Count))

    count = Count.value

    i = 0
    TmccPxWpRecordList = []
    while i < count:
        TmccPxWpRecordList.append(test_TmccPxGetRecordList[i])
        i += 1

    return TmccPxWpRecordList



def Test_TmccPxWpGetCategoryGroup():

    test_PxWpCategory_Group = Test_PxWpCategory_group()
    piCount=c_int(0)
     
    test.TmccPxWpGetCategoryGroup(pointer(test_PxWpCategory_Group), pointer(piCount))
    test.TmccPxWpGetCategoryGroup(pointer(test_PxWpCategory_Group), pointer(piCount))

    lstCategoryGroup = []
    pCount = piCount.value

    i = 0
    while i < pCount:
        lstCategoryGroup.append(i)
        i += 1

    return pCount, lstCategoryGroup

def Test_TmccPxWpGetCategoryName(Categ_Code):
   
    Cagegory_Name = c_char_p()
    test.TmccPxWpGetCategoryName(Categ_Code,Cagegory_Name)
    return Cagegory_Name
    

def Test_TmccPxWpGetCategoryGroupName(Categ_Group_Code):
    CagegoryGroup_Name = c_char_p()
    test.TmccPxWpGetCategoryGroupName(Categ_Code,CagegoryGroup_Name)
    return CagegoryGroup_Name


########################################################
######             General Info              ###########
########################################################

class Test_TmccVerItem_T(Structure):
    _fields_=[("ComponentType",c_int),
              ("ComponentVer",c_char*(TMCC_MAC_MAX_VER_LEN+1)),
              ("auID"        ,c_int),
              ("Update_time",c_int)]

class Test_TmccUpdateVer_T(Structure):
    _fields_=[("list",Test_TmccVerItem_T*(iCORE_MAX_UPDATE_COMPONENT_LISTSIZE)),
              ("Count", c_int)]

class Test_TmccUpdateVer2_T(Structure):
    _fields_=[("list",Test_TmccVerItem_T*(iCORE_MAX_UPDATE_COMPONENT_LISTSIZE)),
              ("Count", c_int)]
 #             


def Test_TmccGetVersion():

    testlist=Test_TmccUpdateVer_T

    tests=testlist()

    nRet=test.TmccGetVersion(pointer(tests))

    print tests.Count
##
    ComponentTypes=[]

    ComponentVers=[]

    UpdateTime=[]

    AUID=[]

    Contents=None
##
    for index in range(0,tests.Count):

        ComponentTypes.append(tests.list[index].ComponentType)

        ComponentVers.append(tests.list[index].ComponentVer)

        AUID.append(tests.list[index].auID)
        #print tests.list[index].ComponentVer

        UpdateTime.append(tests.list[index].Update_time)
        

    Contents=[ComponentTypes,ComponentVers,AUID,UpdateTime]

    return Contents


def Test_TmccSetExpiredFuncMask(funcMask):
    test.TmccSetExpiredFuncMask(funcMask)

                                        
########################################################
######               CallBack                ###########
########################################################                                        

TMCC_PX_HTTP_MAX_NOTIFY_URL_SIZE = 511
TMCC_PX_WEB_PROTECT_MAX_CATEGORY_NAME_LENGTH = 255
TMCC_PX_WEB_PROTECT_MAX_CATEGORY_NAME_LENGTH = 127
##
class Test_TmccPxErrorNotify(Structure):
    _fields_=[("ErrorNum",c_int)]

class Test_TmccSchedScanNotify(Structure):#schedule scan sructure
    _fields_=[("bFoundVirus",c_int)]



class Test_Category(Structure):
    _fields_=[("CategoryCode",c_int),
              ("wszCategoryName", c_char*(TMCC_PX_WEB_PROTECT_MAX_CATEGORY_NAME_LENGTH+1))]
   
class Test_WTP(Structure):
    _fields_=[("szThreat",c_char*(TMCC_PX_WEB_PROTECT_MAX_CATEGORY_NAME_LENGTH+1)),
              ("Threat", c_int)]

class Test_WPScanResult(Union):
    _fields_=[("Category",Test_Category),
              ("WTP", Test_WTP)]

class Test_WPNotify(Structure):#WTP callback structure
    _fields_=[("szURL",c_char*(TMCC_PX_HTTP_MAX_NOTIFY_URL_SIZE+1)),
              ("ScanType", c_uint),
              ("ScanResult",Test_WPScanResult)]


class Test_TimeNotify(Structure):#task time notification
    _fields_=[("tmccTaskTime",c_float)]

class Test_TaskNotify(Structure):#tasknotify
    _fields_=[("countDownSecond",c_int)]

   
class Test_TmccNotify_t(Union):
    _fields_=[("WPNotify", Test_WPNotify)]
    
class Test_NotifyData(Structure):
    _fields_=[("size", c_int),
              ("Data", POINTER(Test_TmccNotify_t))]


class Test_SchedUpdateNotify(Structure):#AU callback 
    _fields_=[("bNeedReload",c_int),
              ("newComponentNum",c_int)]

class Test_InsertDiskNotify(Structure):
    
    _fields_=[("diskpath",c_char*(TMCC_MAC_MAX_PATH_LEN+1))]


class Test_TmccNotify(Union):

    _fields_=[("WPNotify",Test_WPNotify),
              ("SchedScanNotify",Test_TmccSchedScanNotify),
              ("ErrorNotify",Test_TmccPxErrorNotify),
              ("InsertDiskNotify",Test_InsertDiskNotify),
              ("SchedUpdateNotify",Test_SchedUpdateNotify),
              ("TimeNotify",Test_TimeNotify),
              ("TaskNotify",Test_TaskNotify)]
              
              

def RegisterCallBackFunc():
    
    Test_TmccCallbackFunc=CFUNCTYPE(c_int,c_int,POINTER(Test_TmccNotify))
    TmccCallback=Test_TmccCallbackFunc(Test_TmccCallBack)
    nRet=test.TmccRegisterListener(TmccCallback)
    if nRet==0:
        print "##########Register callback####"
        print "Call back func register successfully!!"
    return nRet


def UnRegisterCallBackFunc():
    if test.TmccUnregisterListener()==0:
        print "##########Unregister Callback####"
        print "Callback func unregister successfully!"


def Test_TmccCallBack(cmd,notifyData):
    print "callback notification is comming"
    return 0
    


def Test_TmccInit():

    try:
        nRet=test.TmccInit()
        
    except:
        print "init error"
  
    
def Test_TmccRelease():

    nRet=-1
    
    try:
        nRet=test.TmccRelease()
      
    except:
        print nRet
        print "release error"





##Test_TmccInit()
##
##Test_TmccSendCommand(8,None,None)
##Test_TmccRelease()

