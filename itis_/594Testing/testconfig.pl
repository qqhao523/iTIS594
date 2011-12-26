
our $serverInfo="~/desktop/tmccmac.conf.plist";

###according to the configured source info to change the TmccMac.ini
ChangeAUServerInfo();


sub ChangeAUServerInfo{

    my $updateUrl=$globalCfg->{General}->{Update};
    my $nIndex=0;
    open ServerFile,'~/desktop/test11.txt';
	my @lines=<ServerFile>;
        
        print "lines=@mylines\n";
        close(ServerFile);
      	foreach $line (@lines){
         
	   if($line=~/<Key>Source<\/Key>/i)
	      {
		my $temp=$lines[$nIndex+1];
                print $nIndex;
                print $temp;
                if ($temp=~/.*$updateUrl.*/i){
                        
                	last;
                }
                system("SystemStarter stop iCoreService");

                
                $temp=~s/http.*/$updateUrl<\/string>/;
               
		$lines[$nIndex+1]=$temp;
                if (open(ServerFile,">$serverInfo")){

	            print ServerFile @lines;
                    close (ServerFile);
	         }
     
                system("SystemStarter start iCoreService"); 
                last;
	      }
           $nIndex++;
          
        }
    }   
       
#}
    










