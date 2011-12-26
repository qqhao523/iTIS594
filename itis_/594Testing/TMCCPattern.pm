package TMCCPattern;

use TMCCMacConfig;
use TMCCReport qw(XNote);
use TMCCFunc;
use File::Copy;





sub new {

    TMCCReport::XNote "Enter TMPattern new", __FILE__, __LINE__, 90;

    my $self=shift;
    my $obj={
        curPtn=>'', #ptn number in storage
        tgtPtn=>'', #ptn number in server.ini
        orgPtn=>'', #ptn number before update
        auType=>0, #AU type: [0-unknown],[1-Full download],[2-incremental]
        @_



    };

    bless $obj,$self;

}


sub LoadPattern {
    my $self=shift;

    TMCCReport::XNote "Enter TMPattern",__FILE__, __LINE__, 90;
    TMCCReport::XNote "Enter TMPattern::LoadPattern <$self->{name}>",__FILE__, __LINE__, 90;


    my $try = @_>0 ? shift : 10; #default timer=10 seconds

    unless ($try>=1) {

        $try = 10;
    }
    TMCCReport::XNote $self->{curPtn};
    TMCCReport::XNote $self->{tgtPth};
    TMCCReport::XNote $self->{orgPth};
    #Pattern has been updated
    print $self->{curPtn};
    print $self->{tgtPth};
    if(($self->{curPtn} ne '')&&($self->{curPtn} eq $self->{tgtPtn})) {

        TMCCReport::XNote "Pattern is update to date.", __FILE__, __LINE__, 90;
        TMCCReport::XNote "Leave TMPattern::LoadPattern", __FILE__, __LINE__, 90;
        return 1;
    }

    #save the orginal pattern number

    $self->{orgPtn}=$self->{curPtn};
    TMCCReport::XNote "self->{orgPtn}: $self->{orgPtn}",__FILE__, __LINE__, 90;

    my $ptnDef='pattern.ini';
    my $tempptnInfo = TMCCMacConfig->new()->read($ptnDef) or TMCCReport::XNote "Can't read $ptnDef."
       ."Make sure automation program has access right.", __FILE__, __LINE__, 20;

    TMCCReport::XNote "CurVersion: $self->{name}->{CurVersion}\n",__FILE__, __LINE__, 90;
    $self->{curPtn}=$tempptnInfo->{$self->{name}}->{CurVersion};     #read version number from the pattern.ini
    TMCCReport::XNote "curPtn: $self->{curPtn}\n",__FILE__, __LINE__, 90;


    #print "cur";
    #print $self->{curPtn};
    #print "tgt";
    #print $self->{tgtPtn};

    ##GetCurrentPtn
    my $ret = ($self->{curPtn} < $self->{tgtPtn}) ? 0 : 1;

    TMCCReport::XNote "Leave TMPattern::LoadPattern2. Result: $self->{tgtPtn}",__FILE__, __LINE__, 90;
    TMCCReport::XNote "Leave TMPattern::LoadPattern. Result: $ret. <0: Fail, 1: Success>",
    __FILE__, __LINE__, 90;
    #return if the pattern has been loaded or not
    $ret;


}

sub FindNewPattern {
    my $self = shift;
    my $svrInfo = shift;
    TMCCReport::XNote "Enter TMPattern::FindNewPattern Type:$self->{name}",
    __FILE__, __LINE__, 90;

    $self->{auType} = 0; #unknow Au type;

    my $auId = $self->{auID};
    my $srvPtnVer = '';
    $_ = ${$svrInfo};
    if (/[^;]($auId=[^\,]*\,)([\.\d]*)\,/si) { $srvPtnVer = $2; }#find the pattern in server
    else {
        #impossible!!!
        $srvPtnVer = $self->{tgtPtn};
        TMCCReport::XNote "Can't find pattern information for $self->{name} from server.ini",
        , __FILE__, __LINE__, 20;
    }
    $srvPtnVer =~ s/^[0]*//; #remove leading zero
    $self->{tgtPtn} = $srvPtnVer;

    if ($self->{curPtn} < $self->{tgtPtn}) { #there's new pattern
        #check au type
        my $cur=$self->{curPtn};

        TMCCReport::XNote "Check if incremental pattern exist on server. [1:full, 2:incremental]", __FILE__, __LINE__, 90;
        $self->{auType} = 1;
        $self->{auType} = 2  if (/$auId\.Merge\.[\d]+\=[^\,]*\,$cur\,/si) ;
        TMCCReport::XNote "AU type: $self->{auType}. [1:full, 2:incremental]", __FILE__, __LINE__, 90;

        return 1;
    }
    0;
}


sub NeedUpdate {
    my $self = shift;
    $self->{curPtn} < $self->{tgtPtn} ? 1 : 0; #compare as string
}



#Para  : this is object method. first para is object reference
#Create report facility
#----
sub InitReport {
    my $self=shift;
    TMCCReport::XNote "Enter TMPattern::InitReport", __FILE__, __LINE__, 90;
    #create log facility
    undef $self->{report} if (defined $self->{report});

    if ($::mode =~ /PIT/i) {
        $self->{report} = Create PITReport \$self;
    } else {
        $self->{report} = Create P594Report \$self;
    }
}

sub EnvReport{
    my ($self)=@_;
    TMCCReport::XNote "Enter TMCCPattern::EnvReport",__File__,__LINE__,90;

    $self->{report}->EnvReport();
}

#----
#Para  : this is object method. first para is object reference
#Generat AU report
#----
sub AUReport {
    my ($self, $timer, $rst)=@_;
    TMCCReport::XNote "Enter TMPattern::AUReport", __FILE__, __LINE__, 90;

    $self->{report}->AUReport($timer, $rst);
}


sub ScanReport {
    my $self = shift;
    TMCCReport::XNote "Enter TMPattern::ScanReport", __FILE__, __LINE__, 90;
    $self->{report}->ScanReport(@_);
}

#----
#Para  : this is object method. first para is object reference
#Finalize the report and close the rpt handle
#----
sub CompileReport {
    my $self = shift;
    TMCCReport::XNote "Enter TMPattern::CompileReport", __FILE__, __LINE__, 90;
    $self->{report}->CompileReport(@_);

    undef $self->{report};
}

sub VerifyPattern {
    my $self = shift;
    TMCCReport::XNote "Enter TMPattern::TestPattern. Type: $self->{name}", __FILE__, __LINE__, 90;

    #common definition
    my $MANUAL_SCAN = 0;
    my $REALTIME_MONITOR = 1;

    #remove existing scan log files
    ###my $logExt = $self->{logExt};
    ###my $logPath = $::pccPath.'log';
    ###@fs = grep /.*\.$logExt/i, split /\n/, `dir \"$logPath\\*.*\" /b`;
    ###foreach (@fs) { unlink $logPath.'\\'.$_;}

    #get malicious samples information
    #my malFiles = $self->{malSample}; #virus samples
    my $vNum = $self->{malSample};

    #my $sampleSrc = $::globalCfg->{General}->{SampleFolder}; #virus sample file (compressed)
    my $sampleSrc=$self->{ScanFolder};
    unless (-e $sampleSrc) {
        TMCCReport::XNote "Can't find virus sample files $sampleSrc.", __FILE__, __LINE__, 20;
        return 0;
    }

    $sampleSrc=~/.*\/(.*)\.zip/;
    my $temp=$1;

    #restore malicious samples to current usre's desktop
    my $scanFld = '~/Desktop';
    $scanFld=$scanFld.'/'.$temp;
    #my ($scanFld) = split /;/, $::globalCfg->{General}->{ScanFolder};
    TMCCReport::XNote "restore virus samples to $scanFld", __FILE__, __LINE__, 90;
    system("unzip -o -qq -P virus $sampleSrc -d $scanFld");
    #$sampleSrc= ~/.*\/(.*)\.zip/;


    $TotalMalwares=0;
    $TotalScan=0;
    $detected=0;
    $cleaned=0;
    $Quarantined=0;
    $result=0;


    $normalDetected=0;

    $normalresult=0;
    if($self->{scanType} == $MANUAL_SCAN) {
        TMCCReport::XNote "Perform manual scan", __FILE__, __LINE__, 90;
        #special for TSC: run trjan and change system

        #trigger scan
        my $ScanResult=TMCCFunc::TestTmcc (function=>'Scan', folder=>$scanFld);

        $ScanResult=~/.*:(\d+)\;.*:(\d+);.*:(\d+);.*:(\d+);.*:(\d+);.*:(\d+)/;

        $TotalMalwares=$1;

        $TotalScan=$2;

        $detected=$3;

        $cleaned=$4;

        $Quarantined=$5;

        $result=$6;

        ###### do the normal scan






    } elsif ($self->{scanType} == $REALTIME_MONITOR) {

    }




    TMCCReport::XNote "totall expected: $vNum; detected: $detected, cleaned: $cleaned; Quarantined: $Quarantined",
    __FILE__, __LINE__, 90;
    my @ret = qw(0);

    @ret = qw(1) if $detected >= $vNum and $result==0; #scan successfuly

    if (wantarray) {
        TMCCReport::XNote "Array result expected.", __FILE__, __LINE__, 90;
        push @ret, ($TotalScan, $detected, $cleaned, $Quarantined);
        return @ret;
    }else {
        TMCCReport::XNote "Scalar result expected. Returned: $ret[0]", __FILE__, __LINE__, 90;
        return $ret[0];
    }
}












1;

__END__
