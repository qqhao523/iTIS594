BEGIN {

our $mode = shift;
$_ = shift;

$_='-l=30' if $_ eq '';
##
if (($mode =~ /^\b*(PIT)$/i)&&(/^\-l\=([\d]+)/)) {
##
    our $logLevel = $1;
##
} else {
print <<Usage;
Trend Micro (c) 2007, All Rights Reserved.\n
$0 PIT [-l=logLevel]
Options:
PIT , run with PIT mode
 -l,   level of log to be written to debug log file. Default = 30
       <=10, Status information only
       <=30, Error information and status information
      <=100, All information
\nContactor: maria_zhou\@trendmicro.com\n
Usage
exit;
}}



use TMCCMacConfig;
use TMCCPattern;         #Encapsulate Pattern basic function
use TMCCFunc;            #Call python realize main functions
use File::Copy;
use TMCCReport;          #Report and debug log
use LWP;
use TMCCTimer;           #Calculate start and stop time
use Data::Dumper;

our ($PCC, $VER) = ('iTIS', "1.5"); #TIS general information
our $platform = ""; #OS environment
our $globalCfg;  #configration map from TIS_16-config.ini
our $ptnInfo;    #pattern definition map from pattern.ini
our %patterns;   #pattern objects to be tested
our $logLevel;
our $mode;
our $curRunningStatus;


#add by dewa start
our $NowAUURLNum;
our $NowPatternType;
#add by dewa end


###get platform information####
$tempplat=`sw_vers`;

$tempplat=~/.*:\s*(.*)\n.*:\s*(.*)\n/;

$platform=$1." ".$2;

######end platform information#####

$globalCfg=TMCCMacConfig->new()->read("TMCCMacConfig.ini");

our $serverInfo="/Library/Application\ Support/TrendMicro/common/conf/tmccmac.conf.plist";



#==> Program starts from here
#printf "%-80s", " ";
printf "\n==========================================================================\n";
printf "%-80s\n", "PATTERN INTEGRATION TEST for Trend Smart Surfing 1.5.";
printf "%-80s\n", ">>> Start $mode test. Enter 'Ctrl+C' to quit.";
printf "==========================================================================\n";
printf "\r%-74s%5s", "Initiating ...\n", '\\';

$SIG{INT}=\&TeminateScanAndUpdate;       #if user press ctrl+c,then execute TeminateScanAndUpdate

sub TeminateScanAndUpdate{
    Quit();
}

#testCount("19001_AUcpu.log");
#checkTimeLimit(30*60);
#Quit();


my $count = 0;

while (1)
{
    my $urlNumber=$globalCfg->{General}->{UrlNumber};         # urlNumber=1
        printf "\n==================================================";
        printf "\nThere are %d URLs to be proceed.", $urlNumber;
        printf "\nThis is the %d run.", $count++;

        ##for different url
    for ($i =0;$i < $urlNumber;$i++)
    {
            #$::NowAUURLNum=1;
              $NowAUURLNum=$i;
                my $updateUrl=getURLforAU($i);

                #restoreExistPattern($i);
                #ChangeAUServerInfo($updateUrl);
                InitPatterns();

                #loop for PIT test. Always check new pattern if no request to stop
                #keep the gloable configuration update to date
                $globalCfg=TMCCMacConfig->new()->read('TMCCMacConfig.ini');

                $loop = $globalCfg->{General}->{Loop}; #loop number indecate when to quit

                TMCCReport::XNote "\n>>>>> cycle $count, $loop", __FILE__, __LINE__, 90;

                #if find new ptn on server then perform pattern testing
                if (DetectNewPattern($updateUrl))
                {
                   if(PerformPatternTest($mode,$updateUrl,$i)==0)
                   {
                                quit();
                   }
                   else
                   {
                                #move PIT result to temp foloder
                                #movePITResult($i);
                #makeReport();
                                #send594PITResult($i);
                   }

                }
                else
                {
                   TMCCReport::XNote "Local pattern is update to date. $count cycles passed.\n",__FILE__, __LINE__,10;
                   #movePattern("VSAPI",$i);
                   #movePattern("SSAPTN",$i);
                   sleep($globalCfg->{General}->{Delay});
                }

        }

        #comparePatternSize();
        printf "\n\n";
    #quit if exceed the defined loop number
   $loop==0 ? $count : last if $loop<=$count;
}

TMCCReport::XNote "PIT testing completed!" , __FILE__, __LINE__, 90;
##<== Program ends here
#

sub restoreExistPattern     #non-call
{
        my $i=$_[0];
        printf "\n>>>RestoreExistPattern for url %d (if exist)",$i+1;

    #move all url's pattern from patternDL ,if it exist.
        my $patfile1="patternDL/vsapi/".$i;

    if(-e $patfile1)
        {
                #printf "vsapi pattern file already exist\n";

                my $tFolder1="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/Ptn_Normal/";
                #my $tFolder2="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/Ptn_Mac/";
                #my $tFolder3="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/";

                system("cp -rf ".$patfile1."/lpt* ".$tFolder1);
                #system("cp -rf ".$patfile1."/lpt* ".$tFolder2);
                #system("cp -rf ".$patfile1."/lpt* ".$tFolder3);

                #system("rm -rf ".$patfile1);

                #printf ">>> restore vsapi pattern\n";
        }

        my $patfile2="patternDL/ssaptn/".$i;
        if(-e $patfile2)
        {
                #printf "ssaptn pattern file already exist\n";
                my $tFolder3="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/";

                system("cp -rf ".$patfile2."/ssaptn* ".$tFolder3);

                #system("rm -rf ".$patfile2);

                #printf ">>> restore ssaptn pattern\n";
        }

}

#get the AU URL from TMCCMacConfig.ini (Update,Update1,Update2....)
sub getURLforAU
{
        my $i=$_[0];

        my $updateUrl;
        if($i==0)
        {
                $updateUrl=$globalCfg->{General}->{Update};
        }
        else
        {
                $tmp=sprintf("Update%s",$i);
                $updateUrl=$globalCfg->{General}->{$tmp};
        }

        return $updateUrl;
}


sub trim($);
sub ltrim($);
sub rtrim($);

# Perl trim function to remove whitespace from the start and end of the string
sub trim($)
{
        my $string = shift;
        $string =~ s/^\s+//;
        $string =~ s/\s+$//;
        return $string;
}
# Left trim function to remove leading whitespace
sub ltrim($)
{
        my $string = shift;
        $string =~ s/^\s+//;
        return $string;
}
# Right trim function to remove trailing whitespace
sub rtrim($)
{
        my $string = shift;
        $string =~ s/\s+$//;
        return $string;
}



#there are some location folder in TMCCMacConfig.ini
# "ResultFolder" ,"ResultFolder1¡±£¬¡±ResultFolder2¡°¡£¡£¡£
sub getResultLocation
{
        my $i=$_[0];

        my $locationFolder;
        if($i==0)
        {
                $locationFolder=$globalCfg->{General}->{ResultFolder};
        }
        else
        {
                $tmp=sprintf("ResultFolder%s",$i);
                $locationFolder=$globalCfg->{General}->{$tmp};
        }

        return $locationFol der;
}


sub movePITResult
{
        printf "\n>>> Move pit result to PITResult \n";
        my $i=$_[0];

        $logResultFolder=$globalCfg->{General}->{Logs};   # PIT/logs
        $logTarget=getResultLocation($i);        # ResultFolder=PreOprAU

    $tmpfolder="PITResult/".$logTarget;          # PITResult/PreOprAU
    if(-e $tmpfolder)
    {
            #printf "\nrm -rf ".$tmpfolder;
        system("rm -rf ".$tmpfolder);
    }

        system("mkdir PITResult/".$logTarget);

        my $pcmdline="mv ".$logResultFolder." PITResult/".$logTarget."/";    #move "PIT/logs" to "PITResult/PreOprAU/logs"
        system($pcmdline);
}

#get the current version of "VSAPI" or "SSAPTN" from pattern.ini, the version number has benn stored by LoadPattern
#call by makeReport
sub getNowPatternVerInfo
{
        my $patternType=$_[0];

        my $linenum;
        if($patternType eq "VSAPI")
        {
                $linenum="20";
        }
        else
        {
                $linenum="27";
        }

    open (fp, "pattern.ini") || die("can not open file");
        @recs=<fp>;
        #print "\n[";
        @pair=split(/=/,rtrim($recs[$linenum]));
        close fp;
        return $pair[1];
        #print "]";
}

# get the spend time and report the time
# call by checkResult
sub checkTimeLimit
{
        my $startStr=$_[0];
        my $endStr=$_[1];
        my $limitSeconds=eval($_[2]);
        my $spendtime=0;

        #print $limitSeconds;

                @starttimepair=split(/:/,rtrim($startStr));
                @endtimepair=split(/:/,rtrim($endStr));

                my $timestartsec=(eval(rtrim($starttimepair[1]))*60+eval(rtrim($starttimepair[2])))*60+eval(rtrim($starttimepair[3]));
                my $timeendsec=(eval(rtrim($endtimepair[1]))*60+eval(rtrim($endtimepair[2])))*60+eval(rtrim($endtimepair[3]));

                TMCCReport::XNote "Time Start:$timestartsec",__FILE__, __LINE__, 90;
                TMCCReport::XNote "Time End:$timeendsec",__FILE__, __LINE__, 90;

                if($timeendsec >= $timestartsec)
                {
                        $spendtime=$timeendsec-$timestartsec;
                        #print "\nspendtime:";
                        #print $spendtime;
                        #print "\n";
                }
                else
                {
                    $spendtime=((24*60*60)-$timestartsec)+$timeendsec;
                    #print "\nspendtime:";
                        #print $spendtime;
                        #print "\n";
                }

                TMCCReport::XNote "Spend time:$spendtime",__FILE__, __LINE__, 90;
                if($spendtime > $limitSeconds)        #limitSeconds =30 *60
                {
                        TMCCReport::XNote "Overall time <30min FAIL",__FILE__, __LINE__, 90;
                        return "FAIL";
                }
                else
                {
                        TMCCReport::XNote "Overall time <30min PASS",__FILE__, __LINE__, 90;
                        return "PASS";
                }
}

sub checkResult  #call by makeReport
{
        my $nowPatternType=$_[0];
        $resultversion=getNowPatternVerInfo($nowPatternType);
        $resultfolder=$logTarget=getResultLocation($::NowAUURLNum);  #/PreOprAU
        $resultopattern="FAIL";

        #check scan result
        #print "Now Pattern type:".$nowPatternType."\n";
        # path: .\PITResult\PreOprAU\logs\VSAPI\859550\
        $pathString="PITResult/".$resultfolder."/logs/".$nowPatternType."/".$resultversion."/";

        if(open (fp, $pathString."iTIS_1.5-LOG-".$nowPatternType."_".$resultversion.".log"))
        {
                #$resultopattern="FAIL";

                @recs=<fp>;
                @pair1=split(/:/,rtrim($recs[11]));
                #print $pair1[1];
                @pair2=split(/:/,rtrim($recs[21]));
                #print $pair2[1];
                @pair3=split(/:/,rtrim($recs[29]));
                #print $pair3[1];

                TMCCReport::XNote "Pattern Download:$pair1[1] ",__FILE__, __LINE__, 90;
                TMCCReport::XNote "Scan with new Pattern:$pair2[1] ",__FILE__, __LINE__, 90;
                TMCCReport::XNote "TotalStatus:$pair3[1] ",__FILE__, __LINE__, 90;

                if($pair1[1] eq "SUCCESS" && $pair2[1] eq "SUCCESS" && $pair3[1] eq "SUCCESS")
                {
                        $resultopattern="PASS"; # as a return value

                        #check cpu usage
                        $scanCPUresult=checkCPUUsage("SCAN");
                        if($scanCPUresult eq "FAIL")
                        {
                                print "SCAN CPU Usage > 80!";
                                $resultopattern="FAIL";
                    }

                        $auCPUresult=checkCPUUsage("AU");
                        if($auCPUresult eq "FAIL")
                        {
                                print "AU CPU Usage > 80!";
                                $resultopattern="FAIL";
                        }

                        TMCCReport::XNote "SCAN CPU Usage:$scanCPUresult",__FILE__, __LINE__, 90;
                        TMCCReport::XNote "AU CPU Usage:$auCPUresult",__FILE__, __LINE__, 90;

                        #check 30 min
                        $overallTimeResult=checkTimeLimit(rtrim($recs[27]),rtrim($recs[28]),30*60);
                        if($overallTimeResult eq "FAIL")
                        {
                                print "Overall time > 30min!";
                                $resultopattern="FAIL";
                        }

                }
                else
                {
                        print "Result Fail:";
                        print $pair1[1];
                        print $pair2[1];
                        print $pair3[1];
                }

                close fp;
        }

        return $resultopattern;
}

 # write the result to result.ini
 # call by PerformPatternTest
sub makeReport
{
        my $p594Result=checkResult($::NowPatternType);

        my $projectID;
        my $buildNumber;
        my $targetID;
        if($::NowPatternType eq "VSAPI")
        {
                $projectID="138";
                $buildNumber=substr(getNowPatternVerInfo($::NowPatternType),0,4);
                #$targetID="1437";
                $targetID="5986";
        }
        else
        {
                $projectID="2";
                $buildNumber=substr(getNowPatternVerInfo($::NowPatternType),0,4);
                #$targetID="1438";
                $targetID="5987";
        }


    print "Output 594 format report..";
    open (fp,">Result.ini");
    print fp "[Project_Information]\n";
    print fp "ProjectID=".$projectID."\n";
    print fp "BuildNumber=".$buildNumber."\n";
    print fp "EMailAddress=dewa_hong\@trend.com.tw,jervis_lin\@trend.com.tw,caleb_jiang\@trend.com.tw,jamie_chang\@trend.com.tw\n";
    print fp "ReturnFolder=iTIS1.5\n";
    print fp "ReturnMark=TCMT_GET_RESULT_MAIL_ITIS15\n";
    print fp "[Result]\n";
    print fp "R1=DefinedID_iTIS1.5, TargetID_".$targetID.", ".$p594Result;
    close fp;
}

#workaround for 10.5 machine
sub makeReport2
{
        my $p594Result=checkResult($::NowPatternType);

        my $projectID;
        my $buildNumber;
        my $targetID;
        if($::NowPatternType eq "VSAPI")
        {
                $projectID="138";
                $buildNumber=substr(getNowPatternVerInfo($::NowPatternType),0,4);
                #$targetID="1435"
                $targetID="5599";
        }
        else
        {
                $projectID="2";
                $buildNumber=substr(getNowPatternVerInfo($::NowPatternType),0,4);
                #$targetID="1436";
                $targetID="5593";
        }


    print "Output 594 format report..";
    open (fp,">Result.ini");
    print fp "[Project_Information]\n";
    print fp "ProjectID=".$projectID."\n";
    print fp "BuildNumber=".$buildNumber."\n";
    print fp "EMailAddress=dewa_hong\@trend.com.tw,jervis_lin\@trend.com.tw,caleb_jiang\@trend.com.tw,jamie_chang\@trend.com.tw\n";
    print fp "ReturnFolder=iTIS1.5\n";
    print fp "ReturnMark=TCMT_GET_RESULT_MAIL_ITIS15\n";
    print fp "[Result]\n";
    print fp "R1=DefinedID_iTIS1.5, TargetID_".$targetID.", ".$p594Result;
    close fp;
}

# call by PerformPatternTest
sub send594PITResult
{
        printf "\n>>> Send 594 test result\n";

         my $mailconfigname="temail.ini";
         my $sender="jamie_chang\@trend.com.tw";
         my $receiver="SRV_TW-TCMT\@trend.com.tw;jamie_chang\@trend.com.tw;jervis_lin\@trend.com.tw";
         my $resultfile="Result.ini";
         my $title="Result.ini";

         system("rm -rf ".$mailconfigname);
         system("touch ".$mailconfigname);
         system("echo '[SMTP]' >> ".$mailconfigname);
        system("echo 'Server=211.76.133.7' >> ".$mailconfigname);
        system("echo 'Port=25' >> ".$mailconfigname);
        system("echo '[MAIL]' >> ".$mailconfigname);
        system("echo 'From=".$sender."' >> ".$mailconfigname);
        system("echo 'To=".$receiver.";' >> ".$mailconfigname);
        system("echo 'Source=".$resultfile."' >> ".$mailconfigname);

        system("echo '[HEADER]' >> ".$mailconfigname);
        system("echo 'Subject=".$title.".' >> ".$mailconfigname);
        system("echo 'From=".$sender."' >> ".$mailconfigname);
        system("echo 'To=".$receiver.";' >> ".$mailconfigname);

    my $pcmdline="./temailrh > maillog";  # send email by the tool temailrh
    system($pcmdline);

    ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
    # .\594Result\2009_8_3_2347_Result.ini
    system("mv Result.ini 594Result/".($year+1900)."_".($mon+1)."_".$mday."_".$hour.$min."_Result.ini");

}

sub testCount      #non-call
{
    my $pathString=$_[0];

        my $total=0;
        my $count=0;
        if(open (fp,$pathString))
        {
                @recs=<fp>;

                for($row=0; $row < @recs; $row++)
                {
                        #print $recs[$row];
                    @pair=split(/\]/,$recs[$row]);
                    $total+=eval(trim($pair[1]));
                    $count++;
                }
                print $total;
                print "\n";
                print $count;
                print "\n";
                print $total/$count;
                if(($total/$count)>80)
                {
                        $resultoCPUusage="FAIL";
                }

                close fp;

        }

}


# write AU & Scan log and check if cup usage >80, then move log to .\594Testing\
# call by checkResult
sub checkCPUUsage
{
    my $actionType=$_[0];

        $resultoCPUusage="PASS";

        my $logname;
        if($actionType eq "SCAN")
        {
                $pathString="Scancpu.log";
        }
        else
        {
                $pathString="AUcpu.log";
        }

        my $total=0;
        my $count=0;
        if(open (fp,$pathString))
        {
                @recs=<fp>;

                for($row=0; $row < @recs; $row++)
                {
                        #print $recs[$row];
                    @pair=split(/\]/,$recs[$row]);
                    $total+=eval(trim($pair[1]));
                    $count++;
                }
                #print $total;
                #print "\n";
                #print $count;
                #print "\n";
                #print $total/$count;

                #if the average usage >80, then fail
                if(($total/$count)>80)
                {
                        $resultoCPUusage="FAIL";
                }

                close fp;
                #system("rm -rf ".$pathString);
                ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
                # .\594Testing\2009_8_3_2347_AUcpu.log
                system("mv ".$pathString." 594Result/".($year+1900)."_".($mon+1)."_".$mday."_".$hour.$min."_".$pathString);

        }

        return $resultoCPUusage;
}


sub movePattern    #non-call
{
        my $ptnType=$_[0];
        my $nowUrlNum=$_[1];

        #printf "\n>>>move pattern to temp folder Start \n";
        if($ptnType eq "VSAPI")
        {
                #printf "\n move vsapi pattern..\n";
                my $sourceFolder1="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/Ptn_Normal/";
                #my $sourceFolder2="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/Ptn_Mac/";
                my $sourceFolder3="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/";

                my $targetFolder="patternDL/vsapi/".$nowUrlNum."/";

                if(!(-e $targetFolder))
                {
                        my $pcmdline="mkdir ".$targetFolder;
                        system($pcmdline);
                }

                #printf "1";
                #move ".\patternDL\vsapi\1\" to  "/Library/Application\\ Support/TrendMicro/common/lib/vsapi/Ptn_Normal/"
                my $pcmdline="cp -rf ".$sourceFolder1."/lpt* ".$targetFolder." < /dev/null";
                system($pcmdline);
                system("rm -rf ".$sourceFolder1."/lpt*");

                #printf "2";
                #my $pcmdline="cp -rf ".$sourceFolder2."/lpt* ".$targetFolder." < /dev/null";
                #system($pcmdline);
                #system("rm -rf ".$sourceFolder2."/lpt*");

                #printf "3";
                #my $pcmdline="cp -rf ".$sourceFolder3."/lpt* ".$targetFolder." < /dev/null";
                #system($pcmdline);
                system("rm -rf ".$sourceFolder3."/lpt*");

        }
        else
        {
                #printf "\n move ssaptn pattern..\n";

                my $sourceFolder3="/Library/Application\\ Support/TrendMicro/common/lib/vsapi/";
                my $targetFolder="patternDL/ssaptn/".$nowUrlNum."/";

                if(!(-e $targetFolder))
                {
                        my $pcmdline="mkdir ".$targetFolder;
                        system($pcmdline);
                }

                my $pcmdline="cp -rf ".$sourceFolder3."/ssaptn* ".$targetFolder;
                system($pcmdline);
                system("rm -rf ".$sourceFolder3."/ssaptn*");
        }

}

sub comparePatternSize        #non-call
{
        printf "\n>>>compare pattern start \n";

        my $urlNumber=$globalCfg->{General}->{UrlNumber};

        #compare download pattern this turn....
        my $diff="pass";
        my $nowSize="";
        for ($i =0;$i < $urlNumber;$i++)
    {
                my $patfile="patternDL/vsapi/lpt.".$vsapi_versionArray[$i]."-".$i;
                if(-e $patfile)
                {
                        my @attr=stat($patfile);
                        my $fileSize=$attr[7];
                        printf "\nthere is pattern.".$patfile."\nsize:".$fileSize."\n";

                        if($i==0)
                        {
                                $nowSize=$fileSize;
                        }
                        else
                        {
                                if($nowSize ne $fileSize)
                                {
                                        $diff="fail";

                                }
                        }
                }
        }
        printf "vsapi pattern compare result:".$diff."\n";

        my $diff="pass";
        my $nowSize="";
        for ($i =0;$i < $urlNumber;$i++)
    {
                my $patfile="patternDL/ssaptn/ssaptn.".$ssaptn_versionArray[$i]."-".$i;
                if(-e $patfile)
                {
                        my @attr=stat($patfile);
                        my $fileSize=$attr[7];
                        printf "\nthere is a pattern.".$patfile."\nsize:".$fileSize."\n";

                        if($i==0)
                        {
                                $nowSize=$fileSize;
                        }
                        else
                        {
                                if($nowSize ne $fileSize)
                                {
                                        $diff="fail";
                                }
                        }
                }
        }

        printf "ssaptn pattern compare result:".$diff."\n";
}

#change the AU url of  tmccmac.conf.plist to "updateUrl"
#non-call
sub ChangeAUServerInfo
{
    my $updateUrl=shift @_;
    printf "\n>>>Now AU Url...";
    printf $updateUrl;
    printf "\n";

    my $nIndex=0;

    if (open(ServerFile,$serverInfo))  #read tmccmac.conf.plist
    {
        @lines=<ServerFile>;
        close(ServerFile);
              foreach $line (@lines)
        {
           if($line=~/<Key>Source<\/Key>/i)
              {
                my $temp=$lines[$nIndex+1];

                if ($temp eq $updateUrl)
                {
                        last;
                }

                #printf ">>> stop iCoreService\n";
                #system("SystemStarter stop iCoreService > /dev/null");
                                #system("SystemStarter stop TmccCore");

                $temp=~s/http.*/$updateUrl<\/string>/;

                                $lines[$nIndex+1]=$temp;
                if (open(ServerFile,">$serverInfo")){

                    print ServerFile @lines;
                    close (ServerFile);
                 }

                #sleep(20);
                #printf ">>> start iCoreService\n";
                #system("SystemStarter start iCoreService > /dev/null");
                #system("SystemStarter start TmccCore");
                #sleep(20);

                last;
              }
           $nIndex++;

        }
    }

}



#create TMCCPattern object, then load pattern
#call in the beginning while loop
sub InitPatterns{
    TMCCReport::XNote "Enter InitPattern()", __FILE__, __LINE__, 90;
    my $ptnDef='pattern.ini';

    # execute CurrentPatternVersion.py
    TMCCFunc::GetCurrentVersion();


    $ptnInfo = TMCCMacConfig->new()->read($ptnDef) or TMCCReport::XNote "Can't read $ptnDef."
       ."Make sure automation program has access right.", __FILE__, __LINE__, 20;
    my @ptnTypes = split /,/, $ptnInfo->{PATTERN}->{PatternType};        # virus, spyware
    my @ptn2Test;

    foreach $ptnType (@ptnTypes) {
        @ptn2Test = split /,/, $ptnInfo->{$ptnType}->{Patterns};   #VSAPI, SSAPTN
        foreach (@ptn2Test) {
            $patterns{$_} = new TMCCPattern (
            #my $aaa = new TMCCPattern (
                              name=>$_, #pattern name
                              prjID=>$ptnInfo->{$_}->{TCMT}, #project ID in TCMT
                              auID=>$ptnInfo->{$_}->{AUID},  #AUID in server.ini
                              scanType=>$ptnInfo->{$ptnType}->{ScanType},
                              malSample=>$ptnInfo->{$ptnType}->{MalSamples},
                              execSample=>$ptnInfo->{$ptnType}->{ExeSample},
                              ScanFolder=>$ptnInfo->{$ptnType}->{ScanFolder});
        }
    }
    #Get current version info

        foreach (values %patterns)
        {
                $_->LoadPattern; # compare the current version and target version number
        }

}


#download server.ini and check if there's new pattern available in server.
#call in the beginning while loop
sub DetectNewPattern {

    $updateUrl=shift @_;

    TMCCReport::XNote "Enter DetectNewPattern()",__FILE__, __LINE__, 90;
    my $hasUpdate = 0;

    #get server.ini
    my $ua = LWP::UserAgent->new;
    $ua->timeout($globalCfg->{General}->{Timeout});      # 40s
    if ($globalcfg->{General}->{Proxy}!="")
        {$ua->proxy(['http'], $globalCfg->{General}->{Proxy})};

    TMCCReport::XNote "Proxy: $globalCfg->{General}->{Proxy}; URL: {$updateUrl}/server.ini", __FILE__, __LINE__, 90;
    #printf $updateUrl.'/server.ini';
    my $rsp = $ua->get($updateUrl.'/server.ini');
    my $svr_ini;

    if ($rsp->is_success)
    {
       $svr_ini = $rsp->content;
    }
    else
    {
        my $err = $rsp->status_line;
        printf "\nfailed to get server.ini. $s\n";
        TMCCReport::XNote "failed to get server.ini. $err", __FILE__, __LINE__, 20;
        return 0;
    }

    #check if there's new pattern in server.ini
    foreach $p (values %patterns) {
       if ($p->FindNewPattern(\$svr_ini)) {
            $hasUpdate = 1;
            print "\n";
            TMCCReport::XNote "New pattern detected ($p->{name}: $p->{curPtn}".
            ">>>$p->{tgtPtn})".$p->{scanType}, __FILE__, __LINE__, 20;
            $p->InitReport();
        }
    }

    $hasUpdate;
}

#the main function of PIT
#call in the beginning while loop
sub PerformPatternTest
{
    TMCCReport::XNote "Enter PatternTest()", __FILE__, __LINE__, 90;
    #my $mode = shift;
        my $mode = $_[0];    # PIT
        my $nowUrl = $_[1];
        my $nowUrlNum= $_[2];

    my $cb = $globalCfg->{General}->{cbHandler};
    $cb = 1 unless defined $cb; #1 means reset hunging process
    my $sigHandler = {
        0=>\&DoNothing,
        1=>\&Reset,
        2=>\&Terminate
    }->{$cb};
    my $glbTime = new TMCCTimer( #will alarm when timeout
        name       =>"Global_Timer",
        timeout    =>$globalCfg->{General}->{Threshold}*60, #timeout is in minutes.
        _sigHandler=>$sigHandler);
    $glbTime->StartTimer('CPU'=>0); #not monitor CPU usage

     #download pattern
     #AU Timer, only caculate time, no alarm.
     my $auTimer = new TMCCTimer('name'=>"AU");
     $auTimer->StartTimer('CPU'=>1);

    printf ">>> Downloading pattern ...\n";
    TMCCReport::XNote "Downloading pattern ...", __FILE__, __LINE__, 90;


    $auRet=TMCCFunc::TestTmcc(function=>'AU');     # execute ManuUpdate.py
    TMCCReport::XNote "auRet:". $auRet , __FILE__, __LINE__, 90;

    $auTimer->Complete();
        if ($auRet != 0)
        {
                print "Error happened in the manual update,the program will quit, please check log!\n";
                TMCCReport::XNote "AU was terminated abnormally. This might becase of timeout.",
                __FILE__, __LINE__, 90;
                $auTimer->Complete();
                $glbTime->Complete();
                return 0;
        }
    TMCCReport::XNote "AU Completed!", __FILE__, __LINE__, 90;
    print ">>> AU completed! \n";
    my $scanNorFolder=$globalCfg->{General}->{ScanFolder};

    my $scanTimer = new TMCCTimer('name'=>"Scan");   # create timmer object of scan

    my ($ptn, $auRet);


    foreach $ptn (values %patterns)
    {
        if ($ptn->NeedUpdate)
        {

          #wait PCC to load new pattern in no more than 20 seconds
                        $auRet = $ptn->LoadPattern(20);
                        $ptn->EnvReport();

                        printf "\nVerifying pattern: $ptn->{name}: $ptn->{curPtn}";

            $ptn->AUReport(\$auTimer, $auRet);

            if ($auRet)
                        {
                                #when the new pattern is succeffuly loaded
                                printf "\nVerifying pattern\n";
                TMCCReport::XNote "Verifying pattern: $ptn->{name}: $ptn->{curPtn}"
                , __FILE__, __LINE__, 10;
                $scanTimer->Restart('CPU'=>1);
                @scanRet = $ptn->VerifyPattern;
                my $scanNormalResult=TMCCFunc::TestTmcc(function=>'Scan',folder=>$scanNorFolder); #execute ManualScan.py

                    $scanNormalResult=~/.*:(\d+)\;.*:(\d+);.*:(\d+);.*:(\d+);.*:(\d+);.*:(\d+)/;


                        $::NowPatternType=$ptn->{name};
                        #movePattern($ptn->{name},$nowUrlNum);

                    my $normalDetected=$3;

                    my $normalResult=$6;
                                if ($scanRet[0]==1 and $normalResult==0 and $normalDetected==0)
                                {
                    $scanRet[0]=1;
                }
                else
                                {
                    $scanRet[0]=0;
                }
                push @scanRet, ($normalDetected);
                $scanTimer->Complete();
                #$glbTime->Complete() if 1 == $glbTime->{status};
                $ptn->ScanReport(\$scanTimer, \@scanRet);
                $ptn->CompileReport($mode, \$glbTime);


                sleep(5);

                movePITResult($nowUrlNum);
                makeReport();
                                send594PITResult($nowUrlNum);
                makeReport2();  #Workaround solution for 10.5 machine
                                send594PITResult($nowUrlNum);  #Workaround solution for 10.5 machine

                sleep(5);

            }
        }
        }

   printf ">>> SCAN completed!<<<\n";
   $glbTime->Complete();

   return 1;
}

#call by Quit
sub Reset {
    TMCCReport::XNote "Enter Reset()", __FILE__, __LINE__, 90;
    ###if update is running ,call StopManualUpdate.py to stop update
    my $nRet=-1;
    if ($curRunningStatus==1){

        $nRet=`python StopManualUpdate.py`;



        if(nRet!=0){

            TMCCReport::XNote "The running manual update is stopped with errors.",__FILE__,__LINE__,20;

            $curRunningStatus=0;

        }
}
        ###if scan is running, call StopScan.py to stop scan

        if ($curRunningStatus==2){

            $nRet=`python StopScan.py`;


            if($nRet!=0){

                TMCCReport::XNote "The running manual can is stopped with errorS.",__FILE__,__LINE__,20;

                $curRunningStatus=0;
            }



        }




}

#call by TerminateScanAndUpdate
sub Quit{

    TMCCReport::XNote "Enter Quit()", __FILE__, __LINE__, 90;
    Reset(); #stop hunging pcc process

    TMCCReport::XNote "Script is terminated becasue of ctrl+c. ", __FILE__, __LINE__, 90;
    print "\n";
    exit 1;







}



#
# callback function for timer when it is timeout.
# clear hunging pcc process first then quit script.
#
sub Terminate {
    TMCCReport::XNote "Enter Terminate()", __FILE__, __LINE__, 90;
    Reset(); #stop hunging pcc process
    sleep(5);


    TMCCReport::XNote "Script is terminated becasue of timeout. ".
    "Please check the network connection, CPU usage, pcc.log to determine the cause.", __FILE__, __LINE__, 90;
    print "\n";
    exit 1;

}

#
# callback function for timer when it is timeout.
# donothing, return to orginal script and waiting.
#
sub DoNothing {
    TMCCReport::XNote "Enter DoNothing()", __FILE__, __LINE__, 90;
    TMCCReport::XNote "Timeout happen. Script will continue.", __FILE__, __LINE__, 90;
}





1;

__END__