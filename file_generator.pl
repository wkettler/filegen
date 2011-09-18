#!/usr/bin/perl

#
# Generates unique data sets.
#
# Author: William Kettler
# (c) Dell Computer Inc
#

use strict;
use warnings;
use threads;
use threads::shared;
use Getopt::Long;

##############################
# email 6K-10K
# office 6K-1024K
# medical single 512K
# medical large 10240K-204800K
##############################

my $THREAD_CT = 2;
my $MIN;
my $MAX;
my $QTY;
my $OUTPUT_DIR;
my $SPLIT;
my $ZERO;

my $ext = 'urandom.data';
my $input_file = '/dev/urandom';
my $ct :shared = 0;
my $dir :shared = 0;
my $done : shared = 0;
my $lock :shared;
my @thr = ();

GetOptions (
    'thread-ct=i' => \$THREAD_CT,
    'max-size=i' => \$MAX,
    'min-size=i' => \$MIN,
    'qty=i' => \$QTY,
    'output-dir=s' => \$OUTPUT_DIR,
    'zero' => \$ZERO,
    'split=i' => \$SPLIT
    );

# check command line parameters
if (!$MIN || !$MAX || !$QTY || !$OUTPUT_DIR || !defined($SPLIT)) {
    usage();
}

if ($MAX <= $MIN) {
    print "max-size must be greater than or equal to min-size.\n";
    usage();
}

if (!-d $OUTPUT_DIR) {
    print "Output directory does not exist\n";
    usage();
}

if ($ZERO) {
    $input_file = '/dev/null';
}

# track progress
my $progress = threads->create(\&progress);

# create threads
for (my $i=0; $i<$THREAD_CT; $i++) {
    $thr[$i] = threads->create(\&generate);
}

# exit threads
for (my $i=0; $i<$THREAD_CT; $i++) {
    $thr[$i]->join();
}

$progress->join();

####################
# nothing but functions below
####################
t
sub generate {
    my $size;
    my $path;
    my $fid;
    my $output_file;
    my $tid = threads->tid();

    while (1) {
        {
            lock($lock);
            
            if ($done) {
                return;
            }
            
            # set the current directory and file id
            if ($SPLIT != 0) {
                if ($ct%$SPLIT == 0 && $ct != 0) {
                    $dir++;
                }
                $path = $OUTPUT_DIR . "/" . $dir;
                mkdir($path) unless(-d $path);
                $fid = $ct%$SPLIT;
            }
            else {
                $path = $OUTPUT_DIR;
                $fid = $ct;
            }
            
            if (++$ct == $QTY) {
                $done = 1;
            }
        }

        my $output_file = $path . '/' . sprintf("%09d", $fid) . '_' . $tid . '_' . $ext;
        my $size = $MIN + int(rand($MAX-$MIN));
        
        system("dd if=$input_file of=$output_file bs=1024 count=$size 2> /dev/null");
    }	
};

sub progress {
    my $percent;
    my $numhashes;
    my $columns = &getTerminalSize()->[1];
    my $pbwidth = $columns-20;
    while(1) {
        $percent = sprintf("%.2f", $ct/$QTY*100);
        $numhashes = ($ct/$QTY*$pbwidth);
        printf("\r% -${pbwidth}s% 10s", '#' x $numhashes, "[ " . $percent . "% ]\n");
        if ($ct == $QTY) {
            print "File creation complete!!\n";
            return;
        }
        sleep 5;
    }
};

sub getTerminalSize {
    use Term::ReadKey;
    my ($w, $h) = GetTerminalSize(*STDOUT);
    if (!defined $w || !defined $h) {
        die "Cannot determine terminal size!";
    }
    return [$h, $w];
};

sub usage {
    die "Usage\n";
};
