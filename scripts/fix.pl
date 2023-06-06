#!/usr/bin/perl

use strict;
use warnings;
no warnings qw/uninitialized/;

my $full_list   = shift @ARGV;
my $out_dir     = shift @ARGV;
my $by_id_dir   = 'by_id';
my $gis_ip_path = 'gis_property_info';
$out_dir =~ s/\/$//;

open FILE, '<', $full_list or die "Couldn't open file $full_list: $!";
foreach (<FILE>) {
    chomp;
    my ($pid) = split /,/;
    next unless $pid =~ /^\d+$/;
    my $db_path = "$by_id_dir/$pid";
    if (! -f $db_path) {
        print "No property entry for $pid found\n";
        `wget -O - https://www.cambridgema.gov/propertydatabase/$pid > $out_dir/$pid`;
    }
    my $gis_path = "$gis_ip_path/$pid";
    if (! -f $gis_path) {
        print "No GIS entry for $pid found\n";
        `curl -X POST -d 'm=GetDataListHtml&datatab=PropertyInfo&id=$pid' https://gis.cambridgema.gov/map/Services/SelectionPanel.ashx > $gis_path`;
    }
}
