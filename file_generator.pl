#!/usr/bin/perl
#
# file_generator.pl -- generate unique file datasets
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

##############################
# email 6K-10K
# office 6K-1024K
# medical single 512K
# medical large 10240K-204800K
##############################

my $threads = 1;
my $max = 0;
my $min = 0;
my $qty = 0;
my $dir = '';
my $zero = 0;
my $split = 0;

my $ext = 'urandom.data';
my $input = '/dev/urandom';
my $ct :shared = 0;
my $dir_id :shared = 0;
my $done : shared = 0;
my $lock :shared;
my @thr = ();

GetOptions ( 
    'threads=i' => \$threads,
    'max=i' => \$max,
    'min=i' => \$min,
    'qty=i' => \$qty,
    'dir=s' => \$dir,
    'zero' => \$zero,
    'split=i' => \$split
    ) or usage();

# check command line parameters
if (!$min || !$max || !$qty || !$dir) {
    usage();
}

if ($max < $min) {
    die "Error : max must be greater than or equal to min\n";
}

if (!-d $dir) {
    die "Error : output directory does not exist\n";
}

if ($zero) {
    $ext = 'zero.data';
    $input = '/dev/null';
}

# $dir = File::Spec->rel2abs($dir);

# track progress
my $progress = threads->create(\&progress);

# create threads
for (my $i=0; $i<$threads; $i++) {
    $thr[$i] = threads->create(\&generate);
}

# exit threads
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
    #my $tid = threads->tid();

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
    my $numhashes;
    my $columns = &getTerminalSize()->[1];
    my $pbwidth = $columns-20;
    my $stime = time();
    my $etime;
    while(1) {
        $percent = sprintf("%.2f", $ct/$qty*100);
        $numhashes = ($ct/$qty*$pbwidth);
        printf("\r% -${pbwidth}s% 10s", '#' x $numhashes, "[ " . $percent . "% ]\n");
        if ($ct == $qty) {
            $etime = time();
            print "File creation complete!!\n";
            print "Generated $qty files in " . ($etime - $stime) . " seconds.\n";
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
    die "
$0 -- help

Multi-threaded file generator.

$0 [OPTIONS] --dir=DIRECTORY --max=KBYTES --min=KBYTES --qty=NUMBER

Options : 
     --dir=DIRECTORY         create all files in DIRECTORY
     --max=KBYTES            maximum file size in KBYTES
     --min=KBYES             minimum file size in KBYTES
     --split=NUMBER          number of files per directory. If 0 all files
                             are written in the base DIRECTORY
     --threads=NUMBER        number of worker threads
     --qty=NUMBER            number of files to generate
     --zero                  write from /dev/zero instead of /dev/urandom

Dataset definitions : 
     email 6K-10K
     office 6K-1024K
     medical single 512K
     medical large 10240K-204800K\n";
};
