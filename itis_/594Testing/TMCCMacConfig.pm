package TMCCMacConfig;
use strict;
use warnings;
use vars qw{$VERSION $errstr};
#
#require Exporter;
#our @ISA = qw(Exporter);
#our @EXPORT_OK = qw();
BEGIN {
    
    $VERSION="1.0";
    
    $errstr='';
    
}
  
#create an empty object

sub new{ bless{},shift}

# Create an object form a file

sub read{
    
   
    my $class=ref $_[0] ? ref shift :shift;
    
    #check the file
    my $file=shift or return $class->_error('You didnot specify a file name');

    return $class->_error("File '$file' does not exist")         unless -e $file;
    
    return $class->_error("'$file' is a directory not a file")  unless -f  _;
    return $class->_error("Insufficient permission to read '$file'") unless -r _;
    
    local $/=undef;
        
    open CFG, $file or return $class->_error("Failed to open file '$file':$!");
    
    
    my $contents=<CFG>;
    close CFG;

    $class->read_string($contents);
}

###create an object from a string##########
sub read_string{
    my $class=ref $_[0] ? ref shift :shift;
    my $self=bless {},$class;
    return undef unless defined $_[0];
    ##parse the file
    my $ns    ='_';
    my $counter=0;
    
    foreach ( split /(?:\015{1,2}\012|\015|\012)/, shift ) {
		$counter++;

		# Skip comments and empty lines
		next if /^\s*(?:\#|\;|$)/;

		# Handle section headers
		if ( /^\s*\[(.+?)\]\s*$/ ) {
			# Create the sub-hash if it doesn't exist.
			# Without this sections without keys will not
			# appear at all in the completed struct.
			$self->{$ns = $1} ||= {};
			next;
		}

		# Handle properties
		if ( /^\s*([^=]+?)\s*=\s*(.*?)\s*$/ ) {
			$self->{$ns}->{$1} = $2;
			next;
		}

		return $self->_error( "Syntax error at line $counter: '$_'" );
	}

    $self;
    
}

#error handling

sub errstr{$errstr};

sub _error{$errstr=$_[1];undef}








1;
