#!/usr/bin/perl
#
# file_gen.pl -- generate unique file datasets
#
# Written by William Ketler <william_kettler@dell.com>
#       Copyright (C) 2011, All Rights Reserved
#
# Last update 2011-11-30
#

use strict;
use warnings;
use threads;
use threads::shared;
use Getopt::Long;
use File::Spec;
use Pod::Usage;

##############################
# email 6K-10K
# office 6K-1024K
# medical single 512K
# medical large 10240K-204800K
##############################

my $VERSION = '0.1.0';

my $help    = '';
my $man     = '';
my $version = '';
my $threads = 1;
my $max     = 0;
my $min     = 0;
my $qty     = 0;
my $dir     = '';
my $zero    = 0;
my $split   = 0;

my $ext             = '.data';
my $input           = '';
my $ct :shared      = 0;
my $dir_id :shared  = 0;
my $done : shared   = 0;
my @thr             = ();
my $lock :shared;

GetOptions (
    'help|?'    => \$help,
    'man'       => \$man,
    'version'   => \$version,
    'threads=i' => \$threads,
    'max=i'     => \$max,
    'min=i'     => \$min,
    'qty=i'     => \$qty,
    'dir=s'     => \$dir,
    'zero'      => \$zero,
    'split=i'   => \$split
) or pod2usage(1);

# Check command line parameters.
pod2usage( 1 ) if $help;

pod2usage(
    -exitstatus => 0,
    -verbose    => 2,
) if $man;

if ( $version ) {
    print "$VERSION\n";
    exit;
}
if (!$min || !$max || !$qty || !$dir) {
    pod2usage();
}

if ($max < $min) {
    die "Error : max must be greater than or equal to min\n";
}

if (!-d $dir) {
    die "Error : output directory does not exist\n";
}

if ($zero) {
    $ext   = 'zero' . $ext;
    $input = '/dev/zero';
}
else {
    $ext   = 'urandom' . $ext;
    $input = '/dev/urandom';
}

# Track progress
my $progress = threads->create(\&progress);

# Create threads
for (my $i=0; $i<$threads; $i++) {
    $thr[$i] = threads->create(\&generate);
}

# Exit threads
for (my $i=0; $i<$threads; $i++) {
    $thr[$i]->join();
}

$progress->join();

####################
# nothing but functions below
####################

sub generate {
    my $size;
    my $path;
    my $file_id;
    my $output;

    while (1) {
        {
            lock($lock);
            return if $done;
            
            # set the current directory and file id
            if ($split != 0) {
                $file_id = $ct % $split;
                $dir_id++ if ($file_id == 0 && $ct != 0);
                $path = $dir . "/" . $dir_id;
                mkdir($path) or die "Cannot make directory $path : $!\n" 
                    unless(-d $path);
            }
            else {
                $path = $dir;
                $file_id = $ct;
            }
            
            $output = $path .'/'. sprintf("%09d", $file_id) .'_'. $dir_id .'_'. $ext;

            # signal test is done
            $done = 1 if (++$ct == $qty);
        }

        $size = $min + int(rand($max -$min));
        
        system("dd if=$input of=$output bs=1024 count=$size 2> /dev/null")
            == 0 or die "Cannot create file $output : $!\n";
    }	
};

sub progress {
    my $percent;
    my $stime = time();
    my $etime;
    
    while(1) {
        $percent = sprintf("%.2f", ($ct/$qty)*100);
        print "[ $percent % ]\n";
        if ($ct == $qty) {
            $etime = time();
            print "File creation complete!!\n";
            print "Generated $qty files in " . ($etime - $stime) . " seconds.\n";
            return;
        }
        sleep 5;
    }
};

__END__

=head1 NAME

FileGen - Multi-threaded file generator.

=head1 SYNOPSIS

file_gen.pl [options] --dir=DIRECTORY --max=KBYTES --min=KBYTES --qty=number_format

    Options :
        --help               Show help.
        --man                Show manual.
        --version            Show version.
        --split=NUMBER       Number of files per directory.
        --threads=NUMBER     Number of threads.
        --zero               Write from /dev/zero.

    Dataset definitions : 
        email          6K-10K
        office         6K-1024K
        medical single 512K
        medical large  10240K-204800K

=head1 OPTIONS

=over 8

=item B<--dir>

Aboslute path to the output directory.

=item B<--help>

Prints a brief help message and exits.

=item B<--man>

Prints the manual page and exits.

=item B<--max>

Maximum file size specified in KB.

=item B<--min>

Minimum file size specified in KB.

=item B<--qty>

Number of files to generate.

=item B<--split>

Defines the number of files per directory. The default behavior is to create all files in the base directory.

=item B<--threads>

Number of threads. Additional threads can increase application performance.

=item B<--version>

Prints the program version and exits.

=item B<--zero>

If defined all files will be generated using /dev/null. The default behavior is to write from /dev/urandom.

=back

=head1 DESCRIPTION

B<This program> will generate a specified quantity of files for testing. Each file generated is a random size between the min and max defined values.
=cut
