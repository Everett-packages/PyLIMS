#!/usr/bin/perl
use strict;

my $dbname = "/media/VirtualDisk1/UniRef90/uniref90.ff.pfilt";
my $ncbidir = "/home/everett/Projects/PyLIMS/software/blast-2.2.26/bin";
my $execdir = "/home/everett/Projects/PyLIMS/software/psipred-3.5/bin";
my $datadir = "/home/everett/Projects/PyLIMS/software/psipred-3.5/data";

my $basename = $ARGV[0];
$basename =~ s/\.\w+$//;
my ($rootname) = $basename =~ /([^\/]+)$/;

my $tmproot = 111111111111111 + int rand( 999999999999999 - 111111111111111 + 1 );

`cp -f $ARGV[0] $ARGV[1]/$tmproot.fasta`;

chdir($ARGV[1]);

print stderr "Running PSI-BLAST with sequence...\n";

`$ncbidir/blastpgp -b 0 -j 3 -h 0.001 -d $dbname -i $tmproot.fasta -C $tmproot.chk -o $tmproot.blast`;

print stderr "Predicting secondary structure...\n";

`echo $tmproot.chk > $tmproot.pn`;
`echo $tmproot.fasta > $tmproot.sn`;

`$ncbidir/makemat -P $tmproot`;

print stderr "Pass1 ...\n";

`$execdir/psipred $tmproot.mtx $datadir/weights.dat $datadir/weights.dat2 $datadir/weights.dat3 > $rootname.ss`;

print stderr "Pass2 ...\n";

`$execdir/psipass2 $datadir/weights_p2.dat 1 1.0 1.0 $rootname.ss2 $rootname.ss > $rootname.horiz`;
