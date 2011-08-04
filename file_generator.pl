#!/usr/bin/perl

#
# Generates file sets.
#
# Author: William Kettler
#

use strict;
use warnings;
use threads;
use threads::shared;

my $num_threads = 16;
my $min_file_size = 6;  # in KB
my $max_file_size = 10; # in KB
my $qty = 8000000;
my $output_dir = '/share/email';
my $output_file = 'urandom.data';
my $folder_size = 10240;
my @file_size :shared = ();
my @thr = ();

# generate random file size list
my $range = ($max_file_size - $min_file_size) + 1;
for (my $i=0; $i<$qty; $i++) {
        push(@file_size, $min_file_size + int(rand($range)));
}

# create threads
for (my $i=0; $i<$num_threads; $i++) {
    $thr[$i] = threads->create(\&generate);
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

    #print "Thread $tid started\n";
	
	system("mkdir $output_dir/$tid");

        while (1) {
		
		system("mkdir $output_dir/$tid/$working_dir");
		
		for (my $i=0; $i<$folder_size; $i++) {
        
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

			system("dd if=/dev/urandom of=$output_dir/$tid/$working_dir/$name bs=1024 count=$file_size 2> /dev/null");
		
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

		$progress = sprintf("%03d", 100*($qty-@file_size)/$qty);
		print $progress . "% complete...\n";
		sleep(5);
	}

};
