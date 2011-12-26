#!/usr/bin/env python
#test for c header file transfer to python
#TestApp.py

from ctypes import *
import time
import os, sys
#modify by dewa
#LIBRARYPATH = "/Library/Application Support/TrendMicro/common/lib/libTmccMacClientLib.dylib"
LIBRARYPATH = "/Library/Frameworks/icoreClient.framework/Versions/Current/iCoreClient"


#LIBRARYPATH = "/Users/tmqa/Desktop/TMCC/P4V/Core/TMCC-Mac/Dev/TMCC-Mac-1.0/TMCC-Mac/src/TmccCore/clientlib/build/Release/libTmccMacClientLib.dylib"
#LIBRARYPATH = "/Users/jandeng/P4V/Core/TMCC-Mac/Dev/TMCC-Mac-1.0/TMCC-Mac/src/TmccCore/clientlib/build/Release/libTmccMacClientLib.dylib"
#LIBRARYPATH = "/Library/Application Support/TrendMicro/common/lib/libTmccMacClientLib.dylib"

test = cdll.LoadLibrary( LIBRARYPATH )


########################################################
######                         Define Content                        ###########
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

TMCC_PX_WEB_PROTECT_MAX_LIST_RECORD = 500
TMCC_PX_WEB_PROTECT_MAX_CATEGORY_NAME_LENGTH = 127

TMCC_PX_WEB_PROTECT_MAX_CATEGORY = 128
TMCC_PX_WEB_PROTECT_WTP_THREAT_STRLEN = 64



########################################################
######                         RT & Manual Scan                  ###########
########################################################


class Schd_StartDay(Union):
        _fields_=[("Mday",c_int),
                          ("Wday",c_int)]

class Test_Schedule_t(Structure):
        _fields_=[("RepeatInterval",c_int),
                          ("StarDay",Schd_StartDay),
                          ("StarTime",c_int)]

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
                          ("iScanPerformance", c_int ),
                          ("Action",Test_ScanAction_T)]
        
def Test_TmccInit( ):
        print test.TmccInit( )

def Test_TmccRelease( ):
        try:
                print test.TmccRelease( )
        except:
                print "release"

def Test_TmccSetRTScanOptions( bScanInsertDisk, bScanCompressed, iScanCategory, iFirstAction, iSecondAction ):
        test_ScanOption_T = Test_ScanOption_T()
        
        test_ScanOption_T.bScanCompressed = bScanCompressed
        test_ScanOption_T.Action.ScanCategory = iScanCategory
        test_ScanOption_T.Action.firstAction = iFirstAction
        test_ScanOption_T.Action.secondAction = iSecondAction
        
        print "SetRTSOption"
        print test.TmccSetRTScanOptions(bScanInsertDisk, test_ScanOption_T)


def Test_TmccGetRTScanOptions():
        test_ScanOption_T = Test_ScanOption_T()
        bScanI = c_int()
        print "GetRTSOption"
        print test.TmccGetRTScanOptions(pointer(bScanI), pointer(test_ScanOption_T))

        bScanInsertDisk = bScanI.value
        bScanCompressed = test_ScanOption_T.bScanCompressed 
        iScanCategory = test_ScanOption_T.Action.ScanCategory
        iFirstAction = test_ScanOption_T.Action.firstAction
        iSecondAction = test_ScanOption_T.Action.secondAction

        RTSList = [bScanInsertDisk,bScanCompressed,iScanCategory,iFirstAction,iSecondAction]
        return RTSList
        

def Test_TmccSetManualScanOptions( iScanTargetType, iFileCount, lstFileList, bScanCompressed, iScanCategory, iFirstAction, iSecondAction ):
        print "Into SetMSOpt"
        test_ScanTarget_T = Test_ScanTarget_T()
        test_ScanOption_T = Test_ScanOption_T()

        array = Test_String_t * len(lstFileList)
        print "num of file: ", len( lstFileList )
        T_String = array()
        
        test_ScanTarget_T.ScanTargetType = iScanTargetType
        test_ScanTarget_T.Filcount = len(lstFileList)
        
        print "Before While"
        i = 0
        while i < len(lstFileList):
                T_String[i] = Test_String_t()
                T_String[i].wszString = lstFileList[i]
                T_String[i].lenth = len(lstFileList[i])
                i += 1
        
        print "After While"
        test_ScanTarget_T.FileList = cast(pointer(T_String),POINTER(Test_String_t))
        
        test_ScanOption_T.bScanCompressed = bScanCompressed
        test_ScanOption_T.Action.ScanCategory = iScanCategory
        test_ScanOption_T.Action.firstAction = iFirstAction
        test_ScanOption_T.Action.secondAction = iSecondAction        

        print "Before calling SetMSOpt"
        print test.TmccSetManualScanOptions(test_ScanTarget_T, test_ScanOption_T)


def Test_TmccGetManualScanOptionsCreate():
        test_ScanTarget_T = Test_ScanTarget_T()
        test_ScanOption_T = Test_ScanOption_T()
        test.TmccGetManualScanOptionsCreate(pointer(test_ScanTarget_T), pointer(test_ScanOption_T))

        iScanTargetType = test_ScanTarget_T.ScanTargetType
        iFileCount = test_ScanTarget_T.Filcount

        lstFileList = []   
        i = 0
        while i < iFileCount:
                
                lstFileList.append(test_ScanTarget_T.FileList[i].wszString)
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
        test.TmccGetManualScanOptionsRelease(pointer(test_ScanTarget_T), pointer(test_ScanOption_T))





########################################################
######                          Schedule Scan                        ###########
########################################################

        

def Test_TmccSetSchdScanOptions(iScanTargetType, iFileCount, lstFileList, bScanCompressed, iScanCategory, iFirstAction, iSecondAction, Repeat,day,StartTime):
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

        test_Schedule_T.RepeatInterval = Repeat

        if Repeat == 3:
                test_Schedule_T.StarDay.Wday=day
                test_Schedule_T.StarDay.Mday=0
        elif Repeat == 4:
                test_Schedule_T.StarDay.Mday=day
                test_Schedule_T.StarDay.Wday=0
        else:
                test_Schedule_T.StarDay.Wday = 0
                test_Schedule_T.StarDay.Mday = 0
                
        
        test_Schedule_T.StarTime = StarTime

        test.TmccSetManualScanOptions(test_ScanTarget_T, test_ScanOption_T,test_Schedule_T)


def Test_TmccGetSchdScanOptionsCreate():
        test_ScanTarget_T = Test_ScanTarget_T()
        test_ScanOption_T = Test_ScanOption_T()
        test_Schedule_T = Test_Schedule_t()
        test.TmccGetManualScanOptionsCreate(pointer(test_ScanTarget_T), pointer(test_ScanOption_T),pointer(test_Schedule_T))


def Test_TmccGetSchdScanOptionsRelease():
        test_ScanTarget_T = Test_ScanTarget_T()
        test_ScanOption_T = Test_ScanOption_T()
        test_Schedule_T = Test_Schedule_t()
        test.TmccGetManualScanOptionsRelease(pointer(test_ScanTarget_T), pointer(test_ScanOption_T),pointer(test_Schedule_T))


########################################################
######                         Operation                                 ###########
########################################################

class Test_TmccScanStatus_t(Structure):
        _fields_=[("bRunning",c_int),
                          ("ScanPercent",c_int),
                          ("TotalNum",c_int),
                          ("ScanedNum",c_int),
                          ("ThreatNum",c_int),
                          ("ScanFileName",c_char*(TMCC_MAC_MAX_PATH_LEN+1)),
                          ("Result", c_int)]
                                                                  
class Test_TmccUpdateStatus_t(Structure):
        _fields_=[("bRunning",c_int),
                          ("UpdatePercent",c_int),
                          ("Status",c_int)]


def Test_TmccManualScanStart(lstFileList):
        test_ScanTarget_T = Test_ScanTarget_T()

        array = Test_String_t * len(lstFileList)
        T_String = array()
        
        test_ScanTarget_T.ScanTargetType = 3
        test_ScanTarget_T.Filcount = len(lstFileList)
        
        i = 0
        while i < len(lstFileList):
                T_String[i] = Test_String_t()
                T_String[i].wszString = lstFileList[i]
                T_String[i].lenth = len(lstFileList[i])
                i += 1

        test_ScanTarget_T.FileList = cast(pointer(T_String),POINTER(Test_String_t))
        
        test.TmccManualScanStart(pointer(test_ScanTarget_T))


def Test_TmccGetScanStatus( bSchedScan ):
#        print "Into GetScanStatus"
        test_TmccScanStatus_t = Test_TmccScanStatus_t()

        test.TmccGetScanStatus(bSchedScan, pointer(test_TmccScanStatus_t))
#        print test.TmccGetScanStatus(bSchedScan, None )
#        print test_TmccScanStatus_t.ScanPercent
                     
        return [ test_TmccScanStatus_t.bRunning, test_TmccScanStatus_t.ScanPercent, test_TmccScanStatus_t.TotalNum, test_TmccScanStatus_t.ScanedNum, test_TmccScanStatus_t.ThreatNum, test_TmccScanStatus_t.ScanFileName, test_TmccScanStatus_t.Result]


def Test_TmccGetUpdateStatus():
        test_TmccUpdateStatus_t = Test_TmccUpdateStatus_t()

        test.TmccGetUpdateStatus(c_int, pointer(test_TmccSUpdateStatus_t))



def Test_TmccQuarantineFileOperation(Qitem,Qaction):
        return test.TmccQuarantineFileOperation(Qitem,Qaction)



class Test_TmccCommandResu_t(Structure):
        _fields_=[("resValue",c_int),
                          ("resData",c_char*(TMCC_MAC_MAX_CMD_RESULT_LEN+1))]


def Test_TmccSendCommand(iModuleName,iCommand, lPamrm=None):
        test_TmccCommandResu_t = Test_TmccCommandResu_t()

        #need modification
        if not lPamrm == None:
                lPamrm = None
#        print "SendCommand"
#        print test.TmccSendCommand(iModuleName, iCommand, lPamrm, pointer(test_TmccCommandResu_t))
        return test.TmccSendCommand(iCommand, lPamrm, None )#pointer(test_TmccCommandResu_t))
                                                                                 


####################################################################################
######                         Exception                                 ###########
####################################################################################

def Test_TmccSetScanExceptionList( isEnable, lstExFileList, lstExFileExtList ):
        print "Into Tmcc Set Scan Expt"
        print lstExFileList
        print lstExFileExtList

        arrayFile = Test_String_t * len(lstExFileList)
        T_Exp_File = arrayFile()
        arrayFileExt = Test_String_t * len(lstExFileExtList)
        T_Exp_FileExt = arrayFileExt()

        i=0
        while i<len(lstExFileList):
#                T_Exp_File[i] = Test_String_t()
                T_Exp_File[i].wszString = lstExFileList[i]
                T_Exp_File[i].lenth = len(lstExFileList[i])
                
                i = i+1
                
        j=0
        
        while j<len( lstExFileExtList ):
#                T_Exp_FileExt[j] = Test_String_t()
                T_Exp_FileExt[j].wszString = lstExFileExtList[j]
                T_Exp_FileExt[j].lenth = len(lstExFileExtList[j])
                
                j =j+1
                              
        print "before set Scan Exceptinlist"
        T_Exp_File_P = pointer( T_Exp_File )
        T_Exp_FileExt_P = pointer( T_Exp_FileExt )

        test.TmccSetScanExceptionList( isEnable, T_Exp_File_P, len(lstExFileList), T_Exp_FileExt_P, len(lstExFileExtList) )


def Test_TmccGetScanExceptionListCreate():
        T_Exp_File = Test_String_t()
        T_Exp_FileExt = Test_String_t()
        FileCount = c_int()
        FileExtCount = c_int( )
        isEnable = c_int( )
        
        print test.TmccGetScanExceptionListCreate(pointer(isEnable), pointer(T_Exp_File),pointer(FileCount),pointer(T_Exp_FileExt),pointer(FileExtCount))
       
        print "FileCount", FileCount.value
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
           
#        return len(lstExFileList),lstExFileList,len(lstExFileExtList),lstExFileExtList
        return isEnable.value, lstExFileList, lstExFileExtList


def Test_TmccGetScanExceptionListRelease():
        arrayFile = Test_String_t * len(lstExFileList)
        T_Exp_File = arrayFile()
        arrayFileExt = Test_String_t * len(lstExFileExtList)
        T_Exp_FileExt = arrayFileExt()
                                                                  
        test.Test_TmccGetScanExceptionListRelease(pointer(T_Exp_File),pointer(c_int),pointer(T_Exp_FileExt),pointer(c_int))

                                                                  

########################################################
######                                 AU                                        ###########
########################################################

def Test_TmccSetUpdateSetting(bNeedAutoUpdate, Repeat,day,StartTime):
        test_Schedule_T = Test_Schedule_t()                                                         
        test_Schedule_T.RepeatInterval = Repeat

        if Repeat == 3:
                test_Schedule_T.StarDay.Wday=day
                test_Schedule_T.StarDay.Mday=0
        elif Repeat == 4:
                test_Schedule_T.StarDay.Mday=day
                test_Schedule_T.StarDay.Wday=0
        else:
                test_Schedule_T.StarDay.Wday = 0
                test_Schedule_T.StarDay.Mday = 0
        
        test_Schedule_T.StarTime = StarTime                 
        test.Test_TmccSetUpdateSetting(bNeedAutoUpdate,test_Schedule_T)


def Test_TmccGetUpdateSetting():
        test_Schedule_T = Test_Schedule_t()

        test.Test_TmccGetUpdateSetting(pointer(c_int),pointer(test_Schedule_T))
        


########################################################
######                                 WTP                                   ###########
########################################################


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
                          ("Categories",c_int*128)]

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
        test_TmccProxySetting_t.Protocol = Proto
        test_TmccProxySetting_t.ServerAddress = Server
        test_TmccProxySetting_t.Port = Port
        test_TmccProxySetting_t.bNeedPWD = bNeedPWD
        test_TmccProxySetting_t.UserName = Username
        test_TmccProxySetting_t.Passwor = Password

        test.Test_TmccSetProxySetting(PxyType, bUseSysPxy, test_TmccProxySetting_t)

def Test_TmccGetProxySetting():
        test_TmccProxySetting_t = Test_TmccProxySetting_t()

        test.Test_TmccGetProxySetting(int,pointer(c_int),pointer(test_TmccProxySetting_t))
                                                                  

def Test_TmccPxWpEnable(bEnable,scanType):
        test.TmccPxWpEnable(bEnable,scanType)


def Test_TmccPxWpIsEnabled():
        test.TmccPxWpIsEnabled(pointer(c_int),pointer(c_int))





def Test_TmccPxWTPSetConfig(EnableWtp,wtpLevel,EnableWtpNotify):
        test_TmccPxWTPSet_C = Test_TmccPxWTPSet_C()
        test_TmccPxWTPSet_C.EnableWtp = EnableWtp
        test_TmccPxWTPSet_C.wtpLevel = wtpLevel
        test_TmccPxWTPSet_C.EnableWtpNotify = EnableWtpNotify
        
        test.TmccPxWpWTPSetConfig(pointer(test_TmccPxWTPSet_C))

def Test_TmccPxWTPGetConfig():
        test_TmccPxWTPGet_C = Test_TmccPxWTPSet_C()
        test.TmccPxWpWTPGetConfig(pointer(test_TmccPxWTPGet_C))

  
def Test_TmccPxCatSetConfig(EnableCat,BlockCat,BlockCatNum,EnableCatNotify):
        test_PxWpCategory_C = Test_PxWpCategory_C()

        test_PxWpCategory_C.EnableCategoryChk = EnableCat
        test_PxWpCategory_C.blockCateList.num = BlockCatNum

        i = 0
        while i < len(BlockCat):
                test_PxWpCategory_C.blockCateList.Categories[i] = BlockCat[i]
                i += 1

        test.TmccPxWpCatSetConfig(pointer(test_PxWpCategory_C))        

def Test_TmccPxCatGetConfig():
        test_PxWpCatGet_C = Test_PxWpCategory_C()
        test.TmccPxWpCatGetConfig(pointer(test_PxWpCatGet_C))
        


def Test_TmccPxwpExceptEnable(bEnable,listType):
        test.TmccPxWpExceptEnable(bEnable,listType)


def Test_TmccPxwpExceptIsEnable(bEnable,listType):
        test.TmccPxWpExceptIsEnable(pointer(c_int),pointer(c_int))



def Test_TmccPxSetRecordList(listType,TmccPxWpRecordList,count):
        Array=Test_PxWpRecord*count
        test_PxWpRecord = Array()

        i = 0
        while i < len(TmccPxWpRecordList):
                test_PxWpRecord[i] = Test_PxWpRecord()
                test_PxWpRecord[i].szURL = TmccPxWpRecordList[i]
                i = i+1
        
        test.TmccPxSetRecordList(listType,pointer(test_PxWpRecord),count)

def Test_TmccPxGetRecordList():
        test_TmccPxGetRecordList = Test_PxWpRecord()
        test.TmccPxGetRecordList(pointer(test_TmccPxGetRecordList))



def Test_TmccPxWpGetCategoryGroup():

        test_PxWpCategory_Group = Test_PxWpCategory_group()
        piCount=c_int(0)
         
        test.TmccPxWpGetCategoryGroup(None, pointer(piCount))
        test.TmccPxWpGetCategoryGroup(pointer(test_PxWpCategory_Group), pointer(piCount))

        lstCategoryGroup = []

        i = 0
        while i < pCount:
                lstCategoryGroup.append(i)

        return lstCategoryGroup

def Test_TmccPxWpGetCategoryName(Categ_Code):
   
        Cagegory_Name = c_char_p()
        test.TmccPxWpGetCategoryName(Categ_Code,Cagegory_Name)
        return Cagegory_Name
        

def Test_TmccPxWpGetCategoryGroupName(Categ_Group_Code):
        CagegoryGroup_Name = c_char_p()
        test.TmccPxWpGetCategoryGroupName(Categ_Code,CagegoryGroup_Name)
        return CagegoryGroup_Name


########################################################
######                         General Info                          ###########
########################################################

class Test_TmccVerItem_T(Structure):
        _fields_=[("ComponentType",c_int),
                          ("ComponentVer",c_char*(TMCC_MAC_MAX_VER_LEN+1)),
                          ("Update_time",c_long)]

class Test_TmccUpdateVer_T(Structure):
        _fields_=[("List",POINTER(Test_TmccVerItem_T)),
                          ("ListNum", c_int)]


def Test_TmccGetVersion():
        test_TmccUpdateVer_T = Test_TmccUpdateVer_T()
        test.TmccGetVersion(pointer(test_TmccUpdateVer_T))

def Test_TmccSetExpiredFuncMask(funcMask):
        test.TmccSetExpiredFuncMask(funcMask)

#Test_TmccInit()
#Test_TmccSendCommand( 2, 9 )
#Test_TmccSetSchdScanOptions(iScanTargetType, iFileCount, lstFileList, bScanCompressed, iScanCategory, iFirstAction, i    SecondAction, Repeat,day,StartTime)
#print Test_TmccGetScanExceptionListCreate( )
#print "GetException Complete"
#Test_TmccGetScanExceptionListRelease( )
#print Test_TmccGetManualScanOptionsCreate( )

#Test_TmccSetScanExceptionList( ["a"], [""] )
#test.TmccSetScanExceptionList( None, 0, None, 0  )
#Test_TmccManualScanStart(["/Users/jandeng/Desktop/TMCC/Test/testSample/MS385506"] )
#Test_TmccRelease( )
#print Test_TmccGetManualScanOptionsCreate( )
#Test_TmccGetManualScanOptionsRelease( )
#
##print Test_TmccGetScanStatus( True )
#print Test_TmccSendCommand( 2, 8 )
##time.sleep( 3 )
##print Test_TmccSendCommand( 2, 2 )
###Test_TmccSendCommand( 3, 13 )
##time.sleep( 3 )
##print Test_TmccGetRTScanOptions( )
##Test_TmccSetRTScanOptions( 1, 1, 2, 3, 2 )
##print Test_TmccGetRTScanOptions( )
##Test_TmccSendCommand( 2, 9 )
#try:
#        Test_TmccRelease( )
#except:
#        print "in TmccRelease throw out KeyboardInterrupt"
##print 'a'
##print lstRTSOption
#Test_TmccSetManualScanOptions( 3, 1, ["/12345678"], True, 1, 1, 1)
