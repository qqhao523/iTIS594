<<<<<<<<<<<<<<<<<<<<<<<<<<<<< PIT for TMCCMac 1.0>>>>>>>>>>>>>>>>>>>>>>>>>>
Jan 9,2009. V1.0
A. System Requirement
- Run PIT program
  Mac OS X 10.4.11
  Mac os X 10.5.5
- Run PIT Script
  Perl 5.8.6
  Required perl module:
  - SpreadSheet::WriteExcel
  Python 2.5
===========================================================================
1. Installation
1.1 Install TMCCMac manually
1.1.1 Install Trend Micro Common Client for Mac 1.0 with default settings.(refer readme in the installation package)
1.1.2 From main UI, run manual update, make sure the update can be finished without error.
2. Run PIT testing
2.1 Prepare malware samples and virus samples.
    -Put all malicious samples for testing in a specified folder
2.2 Edit the config file->TMCCMacConfig.ini. Specify proper content for all items under 'General'
  -Delay, Timeout,Update,Logs,Repository,Proxy,Threshold,RepoUser,RepoPass,Loop. The definiti   on for all the items are same as the document "PIT Network Setup and Automation Flow.doc"    defined.
  -For the <scan folder>,define normal folder need to scan.
  -For the <cbHandler>,define what PIT program do when current cycle is timed out.
   0: Do nothing.
   1: Reset hanging process and continuing;
   2: Exit the script.
  -For the <password>,define current administrator's password.
2.3 Edit the pattern config file-> Pattern.ini. Specify proper content for all items to this     file.
  -PatternType: defines the updated pattern type.
  -ScanType:0:manual scan.1:Realtime scan. No realtime scan function for this version.
  -MalSamples:The virus numbers should be scanned.
  -ScanFolder:Regard the different pattern type, the relevant scan folder which include the     malicious samples.
  -AUID: The updated pattern ID number.
  -CurVersion: The current pattern version.
2.4 Prepare log server.
  -Create a shared folder on the log server with/without passwd protection to share with everyone. The shared     folder(Repository)and the relevant user name and password are defined in the config file     "TMCCMacConfig.ini"
  -Using "mount" command to access the shared folder, make sure the user has right to access    accessed & modified without any problems.
2.5 Run PIT program.
  -From termimal, go to PIT folder with bellow command:
    cd PITProgramPath
  -Run PIT program with debug log enabled
    perl TMCCPatternTest.pl PIT -l=90

Reminder:
    About the update and scan funtions, via python script finished.Mainly provide four scripts(manual update, stop manual update, manual scan and stop scan) to realize.
    The CPU usage is realized via  python script(monitor.py) 
         



















      
