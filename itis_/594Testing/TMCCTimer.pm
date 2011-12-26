#!/usr/bin/perl -w


package TMCCTimer;

use TMCCReport;



#@#^!&$&(*^) hop I can have better solution for this dirty global var in future
BEGIN {
    our $timers = undef;
}

sub new {
    my $self = shift;
    my $obj = {
        name=>'',
        timeout=>0,
        _sigHandler =>undef,
        @_
    };
    $obj->{timeout}=0 if $obj->{timeout} < 1;
    $obj->{interval} = 0;
    $obj->{tBegin} = 0; #start time
    $obj->{cpuMonitor} = undef;
    $obj->{status} = 0; #0: unstarted; 1: running; 2: OnTime; 3: Stopped
    TMCCReport::XNote "Create Timer: $obj->{name}, timeout: $obj->{timeout}, "
    , __FILE__, __LINE__, 90;

    bless $obj, $self;
}

sub DESTROY {
    my $self = shift;
    TMCCReport::XNote "Timer: $self->{name} quitting", __FILE__, __LINE__, 90;

    #stop cpu monitor process
    if (defined ($self->{cpuMonitor})) {
        TMCCReport::XNote "Terminate CPU log. Log=$self->{name}.cpu", __FILE__, __LINE__, 90;
        `kill -SIGQUIT $self->{cpuMonitor}`;
        #$self->{cpuMonitor}->GetExitCode($code);
        #$self->{cpuMonitor}->Kill($code);
        $self->{cpuMonitor} = undef;
    }
    #remove cpu log file

    #remove timer from list

}

sub OnTime {
    $ct = time; #current time
#    my $self = shift;

    while (defined($timers)) { #pop up all timeouted timers.
        if ($ct == ${$timers}->{alarm}) {
            TMCCReport::XNote "Timer: ${$timers}->{name} is OnTime!",  __FILE__, __LINE__, 20;
            ${$timers}->{status} = 3; #stopped


            if (defined(ref(${$timers}->{_sigHandler})) 
               && (ref(${$timers}->{_sigHandler}) eq 'CODE')) {
                eval {
                    ${$timers}->{_sigHandler}->(); 
                };
            }

            if (defined (${$timers}->{cpuMonitor})) {
                TMCCReport::XNote "Terminate CPU log. Log=${$timers}->{name}.cpu", __FILE__, __LINE__, 90;
                `kill -SIGINT ${$timers}->{cpuMonitor}`;
                #${$timers}->{cpuMonitor}->GetExitCode($code);
                #${$timers}->{cpuMonitor}->Kill($code);
                ${$timers}->{cpuMonitor} = undef;
            }
        } else {last;}
        if (defined(${$timers}->{nextTimer})) {
            $timers=${$timers}->{nextTimer};
        } else {
           $timers=undef;
        }
    }

    if (defined($timers)) { #contiue to next timer
        #restore to next sig handler
        $SIG{ALRM} = \&TMCCTimer::OnTime;
        print "timeoutinterval=",${$timers}->{alarm} - time;
        alarm(${$timers}->{alarm} - time);
    } else {
        TMCCReport::XNote "All timers are up!",  __FILE__, __LINE__, 90;
        $SIG{ALRM} = 'DEFAULT';
        alarm(0);
    }
    
}

#
#NOTE: TIMERS CAN BE EMBEDED, BUT CAN'T BE OVERLAPPED.
#If the next timeout is behinde the previous one, the previous timer will be
#lost, which never been trigged.
sub StartTimer {
    my $self = shift;
    #print "==>start Timer\n\n";
    my %args = @_;
    TMCCReport::XNote "Start timer: $self->{name}", __FILE__, __LINE__, 90;
    
    ## for the CPU check, do it late!!!!!
    if ($args{CPU} == 1) {
        
        #check and save cpu usage in temp file
        $cpuLog = "$self->{name}cpu.log";
        system("rm $cpuLog") if (-e $cpuLog);
        TMCCReport::XNote "Start CPU monitor. Log=$cpuLog", __FILE__, __LINE__, 90;
        my $cpuId=fork();
        $self->{cpuMonitor} = $cpuId;
        die "Error:$!\n" unless defined $cpuId;     #??????????????
        if(!$cpuId){                              #???????$pid?
            
            exec("python monitor.py $cpuLog");#$pid????0??????(?:$$?????????????PID)
            
        }
    }#????
        
     #   Win32::Process::Create($cpuMonitor, "CPUUsage.exe",
     #                          "CPUUsage /m /log=$cpuLog",
     #                          0, NORMAL_PRIORITY_CLASS|CREATE_NEW_CONSOLE, ".");
       
   
    #else{
    sleep 1; #Make sure the CPU file is generated.

    $self->{status} = 1; #running
    $self->{interval} = 0;
    $self->{tBegin} = time;    
    $self->{timeout} > 0 or return; #timeout argument must be positive.

    TMCCReport::XNote "This timer will be out at ".localtime(time+$self->{timeout}),
    __FILE__, __LINE__, 90;

    #push timer to list(timers)
    $self->{nextTimer}=\${$timers} if defined($timers) or 
    $self->{nextTimer}=undef;

    $timers=\$self;
    $self->{alarm} = time + $self->{timeout};

    #start the timer
    $SIG{'ALRM'} =  \&TMCCTimer::OnTime;

    alarm($self->{timeout});

        
    }  
        
    #}
   
    
        
        
        
#}
    

sub Restart {
    my $self = shift;
    TMCCReport::XNote "Re-Start timer: $self->{name}.", __FILE__, __LINE__, 90;
    my %args = @_;
    $self->Complete();

    defined $args{timeout} ? $self->{timeout}=0 : $self->{timeout}=$args{timeout};
    $self->StartTimer('CPU'=>$args{CPU});
}

sub Complete {
    my $self = shift;
    $self->{interval} = time - $self->{tBegin};
    TMCCReport::XNote "Stop timer: $self->{name}. Interval: $self->{interval} seconds",
    __FILE__, __LINE__, 90;
    $self->{status} = 3; #stopped

    if (defined ($self->{cpuMonitor})) {
        TMCCReport::XNote "Terminate CPU log. Log=$self->{name}.cpu", __FILE__, __LINE__, 90;
        `kill -SIGQUIT $self->{cpuMonitor}`;
        #$self->{cpuMonitor}->GetExitCode($code);
        #$self->{cpuMonitor}->Kill($code);
        $self->{cpuMonitor} = undef;
    }

    $self->{timeout}>0 or return 1;

    #if this timer has timeout, then update the waiting timer list.
    if (defined(${$timers}->{nextTimer})) {
        $timers=${$timers}->{nextTimer};
    } else {
       $timers=undef;
    }

    if (defined($timers)) { #contiue to next timer
        #restore to next sig handler
        $SIG{ALRM} = \&TMTimer::OnTime;
        alarm(${$timers}->{alarm} - time);
    } else {
        TMCCReport::XNote "No waiting timers.",  __FILE__, __LINE__, 90;
        $SIG{ALRM} = 'DEFAULT';
        alarm(0);
    }
}

sub Interval {
    my $self = shift;
    my $interval = {
        0 => 0, #unstarted timer
        1 => time - $self->{tBegin}, #running timer
        2 => time - $self->{tBegin}, #onTime but no 'Complete' called
        3 => $self->{interval} #stopped timer
    }->{$self->{status}};
}

1;

__END__



