#!/usr/bin/perl -w

#######################################################################
#
# chartex - A utility to extract charts from an Excel file for
# insertion into a Spreadsheet::WriteExcel file.
#
# reverse(''), September 2004, John McNamara, jmcnamara@cpan.org
#
# Documentation after __END__
#


use strict;
use OLE::Storage_Lite;
use Getopt::Long;
use Pod::Usage;


my $man         = 0;
my $help        = 0;
my $in_chart    = 0;
my $chart_name  = 'chart';
my $chart_index = 1;
my $sheet_index = -1;
my @sheetnames;
my @exrefs;


#
# Do the Getopt and Pod::Usage routines.
#
GetOptions(
            'help|?'    => \$help,
            'man'       => \$man,
            'chart=s'   => \$chart_name,
          ) or pod2usage(2);

pod2usage(1) if $help;
pod2usage(-verbose => 2) if $man;


# From the Pod::Usage pod:
# If no arguments were given, then allow STDIN to be used only
# if it's not connected to a terminal (otherwise print usage)
pod2usage() if @ARGV == 0 && -t STDIN;




# Check that the file can be opened because OLE::Storage_Lite won't tell us.
# Possible race condition here. Could fix with latest OLE::Storage_Lite. TODO.
#
my $file = $ARGV[0];

open  TMP, $file or die "Couldn't open $file. $!\n";
close TMP;

my $ole      = OLE::Storage_Lite->new($file);
my $book97   = pack 'v*', unpack 'C*', 'Workbook';
my $workbook = ($ole->getPpsSearch([$book97], 1, 1))[0];

die "Couldn't find Excel97 data in file $file.\n" unless $workbook;


# Write the data to a file so that we can access it with read().
my $tmpfile = IO::File->new_tmpfile();
binmode $tmpfile;

my $biff = $workbook->{Data};
print {$tmpfile} $biff;
seek $tmpfile, 0, 0;



my $header;
my $data;

# Read the file record by record and look for a chart BOF record.
#
while (read $tmpfile, $header, 4) {

    my ($record, $length) = unpack "vv", $header;
    next unless $record;

    read $tmpfile, $data, $length;

    # BOUNDSHEET
    if ($record == 0x0085) {
        push @sheetnames, substr $data, 8;
    }

    # EXTERNSHEET
    if ($record == 0x0017) {
        my $count = unpack 'v', $data;

        for my $i (1 .. $count) {
            my @tmp = unpack 'vvv', substr($data, 2 +6*($i-1));
            push @exrefs, [@tmp];
        }

    }

    # BOF
    if ($record == 0x0809) {
        my $type = unpack 'xx v', $data;

        if ($type == 0x0020) {
            my $filename = sprintf "%s%02d.bin", $chart_name, $chart_index;
            open    CHART, ">$filename" or die "Couldn't open $filename: $!";
            binmode CHART;
            printf "\nExtracting \"%s\" to %s", $sheetnames[$sheet_index],
                                                $filename;
            $in_chart = 1;
            $chart_index++;
        }
        $sheet_index++;
    }

    if ($in_chart) {
        print CHART $header, $data;
    }

    # EOF
    if ($record == 0x000A) {
            $in_chart = 0;
    }
}



print "\n\n", ('=' x 60), "\n";
print "Add the following near the start of your program.\n";
print "Change variable name \$worksheet if required.\n\n";

for my $aref (@exrefs) {
    my $sheet1 = $sheetnames[$aref->[1]];
    my $sheet2 = $sheetnames[$aref->[2]];

    my $range;

    if ($sheet1 ne $sheet2) {
        $range = $sheet1 . ":" .  $sheet2;
    }
    else {
        $range = $sheet1;
    }

    $range = "'$range'" if $range =~ /[^\w:]/;

    print "    \$worksheet->store_formula('=$range!A1');\n";
}




__END__
