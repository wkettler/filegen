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

##############################
# email 6K-10K
# office 6K-1024K
# medical single 512K
# medical large 10240K-204800K
##############################

my $num_threads = 8;
my $min_file_size = 512;  # in KB
my $max_file_size = 512; # in KB
my $qty = 100000;
my $output_dir = './data';
my $output_file = 'urandom.data';
my $dir_struct = 0; # 1 if you want a directory structure
my $dir_size = 10240; # number of files per directory when dir_struct is set to 1

my @file_size :shared = ();
my @thr = ();

# generate random file size list
my $range = ($max_file_size - $min_file_size) + 1;
for (my $i=0; $i<$qty; $i++) {
        push(@file_size, $min_file_size + int(rand($range)));
}

# create threads
for (my $i=0; $i<$num_threads; $i++) {
    $thr[$i] = threads->create(\&generate, $dir_struct);
}

# track progress
my $progress = threads->create(\&progress);

# exit threads
for (my $i=0; $i<$num_threads; $i++) {
    $thr[$i]->join();
}

$progress->join();

sub generate {
	my $file_size = 0;
	my $tid = threads->tid();
	my $working_dir = '1';
	my $dir_struct = $_[0];

    #print "Thread $tid started\n";
	
	system("mkdir $output_dir/$tid") if ($dir_struct);

        while (1) {

		system("mkdir $output_dir/$tid/$working_dir") if ($dir_struct);
		
		for (my $i=0; $i<$dir_size; $i++) {
        
			{
				lock(@file_size);
				$file_size = pop(@file_size);
			}

			if (!defined($file_size)) {
				#print "Thread $tid complete.  Processed $num files\n";
				return;
			}
		
			# generate file name
			my $name = sprintf("%06d", $i) . "_" . $tid . "_" . $working_dir . "_" . $output_file;

			if ($dir_struct) {
				system("dd if=/dev/urandom of=$output_dir/$tid/$working_dir/$name bs=1024 count=$file_size 2> /dev/null");
			}
			else {
				system("dd if=/dev/urandom of=$output_dir/$name bs=1024 count=$file_size 2> /dev/null");
			}

		
        }
		
		$working_dir++;
		
		}
};

sub progress {
	my $progress = 0;

	while (1) {
		if (@file_size == 0) {
           print "Complete!\n";
          return;
        }

		$progress = sprintf("%.2f", 100*($qty-@file_size)/$qty);
		print $progress . "% complete...\n";
		sleep(5);
	}

};
