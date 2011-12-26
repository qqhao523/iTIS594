#!/usr/bin/perl -w

package TMCCFunc;

use strict;

use TMCCReport;

 #/nothing running;1:au;2: scan
 
sub TestTmcc{
    TMCCReport::XNote "Entering TMCCFunction::TestTMCC", __FILE__, __LINE__, 90;
    
    
    my %option = @_;
    
    my $result=-1;
    
    if ($option{function} eq 'AU'){
        
        TMCCReport::XNote "The function selection is AU",__FILE__,__LINE__,90;
        
        $::curRunningStatus=1;
                
        $result=`python ManualUpdate.py`;
        #print $result;
        $::curRunningStatus=0;
        
        if ($result==0) {TMCCReport::XNote "The AU function is finished successfully",__FILE__,__LINE__,90 };
        
        return $result;
          
    }
     
    
    elsif($option{function} eq 'Scan') {
        
        my $scanFolder =(exists $option{folder})?$option{folder}:'/Library';
        
        TMCCReport::XNote "Option is Scan; Path: $scanFolder", __FILE__, __LINE__, 90;
        
        $::curRunningStatus=2;
        
        my $ScanResult=`python ManualScan.py $scanFolder`;
        
        $::curRunningStatus=0;
        
        return $ScanResult;
        
        
    }
    
   
    
    
    
    
    
    
    
    
    
    
}

sub GetCurrentVersion{
    
    TMCCReport::XNote "Entering TMCCFunction::GetCurrentVersion", __FILE__, __LINE__, 90;
    
    
    my $nRet=1;
    
    `python CurrentPatternVersion.py`;
 
    
    if (!$nRet){
        
        TMCCReport::XNote "Write version info to patern.ini successfully", __FILE__, __LINE__, 90;
        
        
        
    }
    else{$nRet=1;}
  
    $nRet;
}

1;

__END__