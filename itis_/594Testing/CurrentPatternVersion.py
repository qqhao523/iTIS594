###### for PIT use, get current pattern version########

from TestApp import *

import re

import os

import sys

VIRUS_COMPONENT_INDEX=1


SPYWARE_COMPONENT_INDEX=4

VERSION_FILENAME="pattern.ini"

VIRUS_BEGIN="[VSAPI]"

SPYWARE_BEGIN="[SSAPTN]"

SEARCH_STRING="CurVersion"




def GetPatternVersion():

    #call icoreclient lib
    Components=Test_TmccGetVersion()

    #print Components

    nRet=1

    if Components<>None:

        strVirusV=Components[1][VIRUS_COMPONENT_INDEX]

        strSpyV=Components[1][SPYWARE_COMPONENT_INDEX]

        viList=strVirusV.split(".")

        spyList=strSpyV.split(".")

        strTemp=viList[0]



        for i in range(1,len(viList)):


            strTemp=strTemp+viList[i]

        strVirusV=strTemp

        strVirusV=re.sub("^0","",strVirusV)


        strTemp=spyList[0]

        for i in range(1,len(spyList)):

            strTemp=strTemp+spyList[i]

        strSpyV=strTemp

        strSpyV=re.sub("^0","",strSpyV)


        try:
            versionF=open(VERSION_FILENAME,"r")

            contents=versionF.readlines()

            versionF.close()

            versionF=open(VERSION_FILENAME,'w')

            num=0

            bLine1Exit=False

            bLine2Exit=False

            for eachLine in contents:

                num=num+1

                if bLine1Exit==False:

                    searLine=re.search("^\%s"%VIRUS_BEGIN,eachLine)



                if  bLine2Exit==False:

                    searLine1=re.search("^\%s"%SPYWARE_BEGIN,eachLine)




                if searLine<>None:

                    bLine1Exit=True

                    tempLine=re.sub(SEARCH_STRING+"=.*",SEARCH_STRING+"=%s" %strVirusV,eachLine)

                    if tempLine<>eachLine:
                        searLine=None

                        eachLine=tempLine



                if searLine1<>None:



                    bLine2Exit=True

                    eachLine=re.sub(SEARCH_STRING+"=.*",SEARCH_STRING+"=%s" %strSpyV,eachLine)

                versionF.write(eachLine)


            versionF.close()



        except IOError,e:

            nRet=0
    else:
        nRet=0


    return nRet




if __name__=="__main__":

    Test_TmccInit()

    Ret=GetPatternVersion()

    #print Ret
    nRet=-1
    try:
        nRet=Test_TmccRelease()
    except:
        print nRet



