#!/usr/bin/perl
use strict;

my $dbname = "/home/everett/Projects/PyLIMS/data/system_data/databases/UniProt/sprot.compact_headers";
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

print stderr "$ncbidir/blastpgp -b 0 -j 3 -h 0.001 -d $dbname -i $tmproot.fasta -C $tmproot.chk -o $tmproot.blast\n";
`$ncbidir/blastpgp -b 0 -j 3 -h 0.001 -d $dbname -i $tmproot.fasta -C $tmproot.chk -o $tmproot.blast`;

#if ($status != 0) then
#    tail $tmproot.blast
#    echo "FATAL: Error whilst running blastpgp - script terminated!"
#    exit $status
#endif

print stderr "Predicting secondary structure...\n";

`echo $tmproot.chk > $tmproot.pn`;
`echo $tmproot.fasta > $tmproot.sn`;

`$ncbidir/makemat -P $tmproot`;

#if ($status != 0) then
#    echo "FATAL: Error whilst running makemat - script terminated!"
#    exit $status
#endif

print stderr "Pass1 ...\n";

`$execdir/psipred $tmproot.mtx $datadir/weights.dat $datadir/weights.dat2 $datadir/weights.dat3 > $rootname.ss`;

#if ($status != 0) then
#    echo "FATAL: Error whilst running psipred - script terminated!"
#    exit $status
#endif

print "Pass2 ...\n";

`$execdir/psipass2 $datadir/weights_p2.dat 1 1.0 1.0 $rootname.ss2 $rootname.ss > $rootname.horiz`;

#if ($status != 0) then
#    echo "FATAL: Error whilst running psipass2 - script terminated!"
#    exit $status
#endif
