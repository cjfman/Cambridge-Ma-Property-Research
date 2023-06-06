#!/usr/bin/perl

use strict;
use warnings;
no warnings qw/uninitialized/;

my $dir = shift @ARGV;
my $out = shift @ARGV;
my %rows;
my %columns;
my $running = 1;

$SIG{INT} = sub { $running = 0 };

## Open directory and parse each file
$dir =~ s/\/$//;
opendir DIR, $dir or die "Failed to open $dir: $!";
foreach my $name (readdir DIR) {
    last unless $running;
    parse($name);
}
close DIR;
my @columns = sort keys %columns;

## Write tsv file
print "Writing output to $out\n";
open FILE, '>', $out or die "Failed to open $out: $!";
print FILE join "\t", @columns;
print FILE "\n";
foreach my $row (@rows{sort { $a <=> $b } keys %rows}) {
    print FILE join "\t", @{$row}{@columns};
    print FILE "\n";
}


sub parse {
    my $name = shift;
    my $path = "$dir/$name";
    return unless -f $path;

    print "Reading $path\n";
    my %row;
    open FILE, $path or die "Failed to open $path: $!";
    my $raw = <FILE>;
    close FILE;
    my @divs = split '<div class="ValueSet">', $raw;
    my $key_prefix = '';
    foreach (@divs) {
        if (/Property ID ([^\-]+-[^\-<]+)(-[^<])?/) {
            $row{PropertyID} = "$1$2";
            $columns{PropertyID}++;
        }
        elsif (m{<div class="Label">([\w\s]+)</div>.*<div class="Value">([^>]*)</div>}) {
            my $key = "$key_prefix$1";
            my $value = $2;
            $key =~ s/\s+//g;
            $value =~ s/^\s+|\s+$//g;
            $row{$key} = $value;
            $columns{$key}++;
        }
        elsif (/Owner Information/) {
            $key_prefix = "Owner_";
        }
    }

    ## Fix values
    foreach my $key (qw/LandArea LivingArea/) {
        if (defined $row{$key} && $row{$key} =~ /(\d+) sq ft/) {
            $row{$key} = $1;
        }
    }

    ## Only add row if data was found
    if (defined $row{PID} && defined $row{PropertyID}) {
        $rows{$row{PID}} = \%row;
    }
    else {
        print "Didn't find anything\n";
    }
    close FILE;
}
