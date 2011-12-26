package TMCCReport;
#use strict;
#use warnings;
use File::Copy;

###for 10.5

sub XNote {
    BEGIN {
        our $id=1;
    }

    my ($msg, $file, $line, $level) = @_;

    my ($se,$mi,$ho,$da,$mo,$ye) = localtime time;

    if ($level<=10) {printf "\r%-74s%5s%s", $msg, '', "\b\b\b\b\b"; $id=0}
    elsif ($level <=20) {
        printf "\r%02d\/%02d %02d:%02d:%02d> %-66s", $mo,$da,$ho,$mi,$se, $msg;
        $id=0;
    } else {
        if ($id<5) { print ">" }
        else { printf "%s%s%s", "\b\b\b\b\b", "     ", "\b\b\b\b\b" }
    }
    $id = (++$id)%6;
    my $logpath =$::globalCfg->{General}->{Logs};      #PIT/logs

    if ((defined $logpath)&&($logpath ne '')) {
        (-e $logpath) or system("mkdir -p $logpath");
    } else {
        #PIT can't run without log facility!!!
        die "Please specify proper folder for logs in configuration file.\n";
    }

    #write log to debug log file
    if ($level <= $::logLevel) {


        #create new log file every day
        my $logF = sprintf($logpath."/Debug/$::PCC\_$::VER-DEBUG_LOG-%02d%02d%02d.log",
                           $ye-100, $mo+1, $da);
        (-e $logpath."/Debug") or system("mkdir -p $logpath/Debug");

        #my $logF=$logpath."/Debug/$::PCC/\_$::VER-DEBUG_LOG-%02d%02d%02d.log

        #<=10, status; <=30, error/warning; <=100, information
        if($level<=10){$type='sss'}elsif($level<=30){$type='www'}else{$type='iii'};
        open(F, ">>", $logF) or print "$!\n";
        printf F "%02d\/%02d\/%02d %02d:%02d:%02d <$type> $msg($file line:$line)\n",
                 $ye-100,$mo+1,$da,$ho,$mi,$se;
        close F;
    }
}

package PITReport;
use File::Copy;
our @ISA=qw(TMCCReport);
our $host = "";
#
#this is a constructor
sub Create {
    TMCCReport::XNote "Enter PITReport::Create()", __FILE__, __LINE__, 90;
    my ($self, $ptn) = @_;

    unless (defined $ptn) {
        TMCCReport::XNote "Pattern is required to create report.", __FILE__, __LINE__, 90;
       return undef;
 }

  my $obj = {
      ptn=>$ptn,
      name=>${$ptn}->{name},
      rst=>'SUCCESS'
 };
#
   #initiate log facility
 $logpath =$::globalCfg->{General}->{Logs};
 if (defined $logpath) {
       (-e $logpath) or system("mkdir -p $logpath");
  } else {
        #PIT can't run without log facility!!!
       die "Please specify proper folder for logs in configuration file\n";
    }
    #Text file (Test Result)
    $logpath = $logpath."/${$ptn}->{name}/${$ptn}->{tgtPtn}";
    (-e $logpath) or system("mkdir -p $logpath");
    $logf = $logpath."/$::PCC\_$::VER-LOG-${$ptn}->{name}_${$ptn}->{tgtPtn}.log";
    system("rm $logf") if (-e $logf);
    my ($hn) = split /\n/, `hostname`;

    $host = $::platform.'-'.$hn;

    TMCCReport::XNote "Init PIT result file: $logf", __FILE__, __LINE__, 90;
    open(F,">",$logf);
    print F "---------------------------$host---------------------------";
    close F;
    $obj->{rstLog} = $logf;

#    #excel file (CPU usage chart)
    $logf = $logpath."/$::PCC\_$::VER-CPU_Usage-${$ptn}->{name}_${$ptn}->{tgtPtn}.xls";
#
    TMCCReport::XNote "Init PIT CPU chart file: $logf", __FILE__, __LINE__, 90;
    system("rm $logf") if (-e $logf);
    $obj->{cpuLog} = $logf;
#
##    push @rpt, \$obj;
  bless $obj, $self;
}
#
sub DESTROY {
  my $self = shift;
   TMCCReport::XNote "Test report of pattern $self->{name} is completed.", __FILE__, __LINE__, 90;
}
#
sub EnvReport{

    TMCCReport::XNote "Enter PITReport::EnvReport()",__FILE__,__LINE__,90;
    my ($self)=@_;
     unless (-e $self->{rstLog}) {
        TMCCReport::XNote "No $self->{rstLog} exist.", __FILE__, __LINE__, 20;
    }

    my $ProductName=$::globalCfg->{General}->{ProductName};
    my $cputype=`system_profiler |grep CPU\\ Type`;
    if (!$cputype){
        $cputype=`system_profiler |grep Processor\\ Name`;

    }

    my @cputype1=split(/:/,$cputype);
    $cputype=$cputype1[1];
    $cputype=~s/\n//;
    my $osInfo=`system_profiler |grep System\\ Version`;
    my @osInfo1=split(/:/,$osInfo);
    $osInfo=$osInfo1[1];
    $osInfo=~s/\n//;
    $cputype=~s/^\s+//;
    $osInfo=~s/^\s+//;

    #add by dewa
    my $updateAddress;

    if($::NowAUURLNum==0)
    {
            $updateAddress=$::globalCfg->{General}->{Update};
    }
    else
    {
                $tmp=sprintf("Update%s",$::NowAUURLNum);
                $updateAddress=$::globalCfg->{General}->{$tmp};
    }
        #add by dewa

    print "\nNow AU URL:".$updateAddress."\n";


    open(LOG, ">>", $self->{rstLog});
    print LOG <<eol;
\n>>>>Product Environment
  Product                     :$ProductName
  CPU Type                    :$cputype
  Platform                    :$osInfo
  Update Server               :$updateAddress
eol
    close LOG;




}

sub AUReport {

    TMCCReport::XNote "Enter PITReport::AuReport ()", __FILE__, __LINE__, 90;
    my ($self, $timer, $rst) = @_;

    $self->{auTimer} = ${$timer}->{name};

    ($bs,$bm,$bh) = localtime(${$timer}->{tBegin});
    ($es,$em,$eh) = localtime(${$timer}->{tBegin}+${$timer}->Interval());
    $ptn = $self->{ptn};
    my $rsts = 'SUCCESS';
    if(not $rst) { $rsts='FAIL'; $self->{rst}='FAIL' }

    my $auType = {
        0=>'UNKNOW',
        1=>'Full Update',
        2=>'Incremental Update'
    }->{${$ptn}->{auType}};

    unless (-e $self->{rstLog}) {
        TMCCReport::XNote "No $self->{rstLog} exist.", __FILE__, __LINE__, 20;
    }

    TMCCReport::XNote "Update AU Result. $rsts", __FILE__, __LINE__, 90;
    open(LOG, ">>", $self->{rstLog});
    print LOG <<eol;
\n>>>>Pattern Download
  Latest/Current Pattern      :${$ptn}->{tgtPtn}
  Previous Pattern            :${$ptn}->{orgPtn}
  Pattern Download Type       :$auType
  Result                      :$rsts
  Update Time Start           :$bh:$bm:$bs
  Update Time End             :$eh:$em:$es
eol
    close LOG;
}




sub ScanReport {
    TMCCReport::XNote "Enter PITReport::ScanReport(). @_", __FILE__, __LINE__, 90;
    my ($self, $timer, $rst) = @_;

    $self->{scanTimer} = ${$timer}->{name};

    ($bs,$bm,$bh) = localtime(${$timer}->{tBegin});
    ($es,$em,$eh) = localtime(${$timer}->{tBegin}+${$timer}->Interval());

    my $rsts = 'SUCCESS';
    my ($ret, $tt, $md, $mc, $mq,$nmd) = @{$rst};
    if( $ret<1) { $rsts='FAIL'; $self->{rst}='FAIL' }

    unless (-e $self->{rstLog}) {
        TMCCReport::XNote "No $self->{rstLog} exist.", __FILE__, __LINE__, 20;
    }

    TMCCReport::XNote "Update Pattern Scan Result. $rsts", __FILE__, __LINE__, 90;
    open(LOG, ">>", $self->{rstLog});
    print LOG <<eol;
\n>>>>Pattern Test (Detection/Cleanup) result
  Expected Total              :$tt
  Malware Detected            :$md
  Malware Cleaned             :$mc
  Malware Qurantined          :$mq
  Normal file Detected        :$nmd
  Result                      :$rsts
  Scan Time Start             :$bh:$bm:$bs
  Scan Time End               :$eh:$em:$es

eol
    close LOG;
}


sub CompileReport {

    my $self = shift;
    TMCCReport::XNote "Enter PITReport::CompileReport ()", __FILE__, __LINE__, 90;
    my ($mod, $timer) = @_;

    ($bs,$bm,$bh) = localtime(${$timer}->{tBegin});
    ($es,$em,$eh) = localtime(${$timer}->{tBegin}+${$timer}->Interval());

    unless (-e $self->{rstLog}) {
        TMCCReport::XNote "No $self->{rstLog} exist.", __FILE__, __LINE__, 20;
    }
    #finalize the test result
    open(LOG, ">>", $self->{rstLog});
    print LOG <<eol;
\n>>>>PIT Test Result
  Overall Time Start          :$bh:$bm:$bs
  Overall Time End            :$eh:$em:$es
  Result                      :$self->{rst}\n
eol
    close LOG;

    #finalize the CPU chart
    unshift @INC, './excelchart';
    require Spreadsheet::WriteExcel;
    require Spreadsheet::WriteExcel::Utility;
    require Spreadsheet::ParseExcel;

    my $cpuRpt = Spreadsheet::WriteExcel->new($self->{cpuLog});
    my $auSheet = $cpuRpt->add_worksheet(); #Sheet1

    $auSheet->store_formula('=Sheet1!A1');


    $cpuRpt->add_chart_ext('./data/chart1.bin', "Test-AU-OS");
    $cpuRpt->add_chart_ext('./data/chart2.bin', "Test-Scan-OS");
    $auSheet->write(0, 0, $host);

    my (@auTime, @auCpu);
    my $auCpu = "$self->{auTimer}cpu.log";
    unless (-e "$auCpu") {
        TMCCReport::XNote "Can't find CPU log file for AU. ($auCpu)", __FILE__, __LINE__, 20;
        return 0;
    }
    open(CPU, "<", "$auCpu");
    $count = 1;
    foreach (<CPU>) {
        chomp;
        push @auTime, $count++;
        push @auCpu, (split)[-1];
    }
    close CPU;
    $auSheet->write_col('B1', \@auTime);
    $auSheet->write_col('C1', \@auCpu);

    my (@scanTime, @scanCpu);
    my $scanCpu = "$self->{scanTimer}cpu.log";
    unless (-e "$scanCpu") {
        TMCCReport::XNote "Can't find CPU log file for scan. ($scanCpu)", __FILE__, __LINE__, 20;
        return 0;
    }
    open(CPU, "<", "$scanCpu");
    $count = 1;
    foreach (<CPU>) {
        chomp;
        push @scanTime, $count++;
        push @scanCpu, (split)[-1];
    }
    close CPU;
    $auSheet->write_col('D1', \@scanTime);
    $auSheet->write_col('E1', \@scanCpu);
    $cpuRpt->close();

    #update log file on server
    TMCCReport::XNote "PIT Report: Send report to central server....", __FILE__, __LINE__, 90;

    #print "[";
    #print $::NowAUURLNum;
    #print $NowAUURLNum;
    #print "]";

    #add by dewa
    my $unc;
    if($::NowAUURLNum==0)
    {
            $unc = $::globalCfg->{General}->{Repository};
    }
    else
    {
            $tmp=sprintf("Repository%s",$::NowAUURLNum);
                $unc=$::globalCfg->{General}->{$tmp};
    }
    #add by dewa


    #my $unc = $::globalCfg->{General}->{Repository};
    unless (defined $unc) {
        TMCCReport::XNote "No Repository defined in configuration file. ".
        "Can't put log to central server.", __FILE__, __LINE__, 20;
        return 0;
    }
    TMCCReport::XNote "Central Server Address: $unc", __FILE__, __LINE__, 90;
    ######changed########

    #add by dewa
    my $remoteUser;
    my $pass;
    if($::NowAUURLNum==0)             # local server
    {
            $remoteUser=$::globalCfg->{General}->{RepoUser};       #  dewa
            $pass=$::globalCfg->{General}->{RepoPass};             # 1234
    }
    else                               # web s
    erver 10.64.3.199
    {
            $tmp=sprintf("RepoUser%s",$::NowAUURLNum);             # RepoUser1
            $remoteUser=$::globalCfg->{General}->{$tmp};           # maria_zhou

            $tmp=sprintf("RepoPass%s",$::NowAUURLNum);             # RepoPass1
            $pass=$::globalCfg->{General}->{$tmp};                 # Good!wzhypz!9
    }
    #add by dewa

    $pass=quotemeta($pass);
    $remoteUser=quotemeta($remoteUser);
    my $tempPath="~/documents/PITServer";         #put the pit test result in ~/documents/PITServer
    my $mountedServer=$tempPath;
    (-e $tempPath) or system("mkdir -p $tempPath");
    $_ = $self->{rstLog};
    #my $srvPath = $unc."\\".$1 if /($self->{name}.*\\)([^\\]*)$/i;
     my @testPath1=split("/",$unc);
    my $size=@testPath1;
    my $TrunPath;
    my $mountPath1;
    if ($size>2){
        $TrunPath=$testPath1[0]."/".$testPath1[1];
    }

    (!system("mount -t smbfs //$remoteUser:$pass\@$TrunPath  $tempPath")) or TMCCReport::XNote "Mount remote shared server error.",__FILE__,__LINE__,20;
    my $mountPath1=$TrunPath;
    if ($size>2){
        $TrunPath=$testPath1[2];
            for($i=3;$i<$size;$i++){
           $TrunPath=$TrunPath."/".$testPath1[$i];
        }
    }


    my $tempMount=$tempPath."/".$TrunPath;

    if(!`test -d $tempMount`)
   {
         system("mkdir -p $tempMount");
   }

    my $srvPath=$tempMount."/".$1 if /($self->{name}.*\/)([^\/]*)$/i;
    ######end#######################################
    my $logf = $2;
    my $src=$self->{rstLog};

    my $dest= $srvPath.$logf;
    my $temppath="temp";
    my $temp1=$temppath."/".$logf;

    (-e $srvPath) or system("mkdir -p $srvPath");

    if (!system ("test -e $dest ")) {

        #other machines has completed testing
        TMCCReport::XNote "Update log report of current pattern on server.", __FILE__, __LINE__, 90;

        (-e $temppath) or system("mkdir $temppath");

        if(!(system("test -d $temppath "))){

            `rm -rf $temppath/*.*`;
        }

        `cp -f $dest $temp1`;
        open(LLOG,"<",$src);
        open(SLOG, ">>", $temp1);
        syswrite SLOG, $_ while sysread(LLOG, $_, 1000);
        close(SLOG);
        close(LLOG);
        `cp -f $temp1 $dest`;
    } else {
        #the first log

         (!system ("cp -f $src $dest") )or TMCCReport::XNote "can't copy $self->{rstLog} to $srvPath$logf. ($!)",__FILE__,__LINE__,20;
        #system("cp  $self->{rstLog}  $srvPath.$logf");
        TMCCReport::XNote "This is the first log report for current pattern.", __FILE__, __LINE__, 90;




    }

    TMCCReport::XNote "Update excel chart on server...", __FILE__, __LINE__, 90;
    $_ = $self->{cpuLog};
    #$srvPath = $unc."\\".$1 if /($self->{name}.*\\)([^\\]*)$/i;
    #$srvPath=$tempPath."/".$1 if /($self->{name}.*\/)([^\/].*)$/i;
    $srvPath=$tempMount."/".$1 if /($self->{name}.*\/)([^\/]*)$/i;
    $logf = $2;
    $temp1=$temppath."/".$logf;
    $dest=$srvPath.$logf;
    if (!system("test -e $dest")) {
        TMCCReport::XNote "Update excel chart report of current pattern on server.", __FILE__, __LINE__, 90;
        eval {
        #append cpu usage to file on server
        my $oExcel = new Spreadsheet::ParseExcel;
        `cp -f $dest $temp1`;

        my $oBook = $oExcel->Parse($temp1);
        $oWks = $oBook->{Worksheet}[0];
        unless ($oWks->{MaxCol} > $oWks->{MinCol}) {
           TMCCReport::XNote "$srvPath.$logf is invalid. Replace with local chart file.",
           __FILE__, __LINE__, 20;
            $src=$self->{cpuLog};
            $dest=$srvPath.$logf;
           `cp -f $src $dest`or TMCCReport::XNote "can't copy $self->{cpuLog} to $srvPath$logf.\n$!",__FILE__, __LINE__, 20;
        #    #copy($self->{cpuLog}, $srvPath.$logf) or
            system("umount $mountedServer");
        #
            return;
        #
        }
        #

        #update into a temp file first
        my $bak1=$temppath."/"."PCC_Temp.xls";
        #my $bak = $srvPath."PCC_Temp.xls";
        my $svrRpt = Spreadsheet::WriteExcel->new($bak1);
        my $svrSht = $svrRpt->add_worksheet();

        my ($minR, $maxR) = ($oWks->{MinRow}, $oWks->{MaxRow});
        #update platform information
        my @OSs;
        for ($iR=$minR; $iR <= $maxR; $iR++) {
            $oWkc = $oWks->{Cells}[$iR][0];
            push @OSs, $oWkc->{Val} if ($oWkc);
        }
        push @OSs, $host;
        $svrSht->write_col('A1', \@OSs);
        #copy existing CPU usage information
        for ($iC=1; defined $oWks->{MaxCol} && $iC <= $oWks->{MaxCol}; $iC++) {
            for ($iR=$minR; $iR <= $maxR; $iR++) {
                $oWkc = $oWks->{Cells}[$iR][$iC];
                $svrSht->write($iR, $iC, $oWkc->{Val}) if ($oWkc);
            }
        }
        #append cpu usage information of current (local) testing.
        my $OSs = @OSs;
        my $colName = Spreadsheet::WriteExcel::Utility::xl_rowcol_to_cell(0, $OSs*4-3);
        $svrSht->write_col($colName, \@auTime);
        $colName = Spreadsheet::WriteExcel::Utility::xl_inc_col($colName);
        $svrSht->write_col($colName, \@auCpu);
        $colName = Spreadsheet::WriteExcel::Utility::xl_inc_col($colName);
        $svrSht->write_col($colName, \@scanTime);
        $colName = Spreadsheet::WriteExcel::Utility::xl_inc_col($colName);
        $svrSht->write_col($colName, \@scanCpu);

        #create charts
        $svrSht->store_formula('=Sheet1!A1');
        my $ichart = 1;
        my $i=0;
        foreach (@OSs) {
            $os = $OSs[($ichart-1)/2];
            $i++;
            $svrRpt->add_chart_ext('./data/chart'.$ichart.'.bin', "Test-AU-OS".$i);
            $ichart++;
            $svrRpt->add_chart_ext('./data/chart'.$ichart.'.bin', "Test-SCan-OS".$i);
            $ichart++;



        }
        $svrRpt->close();

        `cp -f $bak1  $dest`;
        #replace the orginal report with latest one
        unlink $srvPath.$logf;
        unlink $bak;
        }; if ($@) {
            TMCCReport::XNote "Get exception when creating CPU chart on log server.\n Error: $@",
            __FILE__, __LINE__, 20;
        }
    } else {
        TMCCReport::XNote "This is first excel chart report of current pattern on server.", __FILE__, __LINE__, 90;
        $src=$self->{cpuLog};
        $dest=$srvPath.$logf;
        (!system("cp  $src $dest")) or TMCCReport::XNote "can't copy $self->{cpuLog} to $srvPath.$logf.\n$!",__FILE__,__LINE__,20;

    }

    ####unmount server info#######

    system("umount $mountedServer");
}












1;

__END__
