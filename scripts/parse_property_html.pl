#!/usr/bin/perl

use strict;
use warnings;
no warnings qw/uninitialized/;

my $dir = shift @ARGV;
my $out = shift @ARGV;
my %rows;
my $running = 1;

$SIG{INT} = sub { $running = 0 };

## Most of these match table data IDs in the property db files
my @columns = qw/
    PropId
    lblAddress
    PropertyClass
    StateClassCode
    Zoning
    MapLot
    MapLot
    LandArea
    YOA
    TaxDistrict
    ResExempt
    BuildingValue
    LandValue
    AssessedValue
    SalePrice
    BookPage
    SaleDate
    PrevAssessedValue
    Owner
    Style
    Occupancy
    NumStories
    FloorLocation
    View
    LivingArea
    NumberOfUnits
    TotalRooms
    Bedrooms
    Kitchens
    FullBaths
    HalfBaths
    Fireplaces
    Flooring
    Layout
    LaundryInUnit
    HeatType
    YearBuilt
    OverallCondition
    OverallGrade
    OpenParking
    CoveredParking
    GarageParking
    FirstFloor_GrossArea
    PropertyImageLink
    gis
/;


## These all match subarea table data IDs
my @subareas = qw/
    SA_Code
    SA_Description
    SA_GrossArea
    SA_LivingArea
    SA_TotalGross
    SA_TotalLiving
/;

## Open directory and parse each file
$dir =~ s/\/$//;
opendir DIR, $dir or die "Failed to open $dir: $!";
foreach my $name (readdir DIR) {
    last unless $running;
    parse($name);
}
close DIR;

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
    my $subarea; ## Keep track of subarea
    foreach (<FILE>) {
        ## Check all column names
        foreach my $col (@columns) {
            if (/<td.*$col.*>(.*)<\/td/) {
                $row{$col} = $1;
                last;
            }
        }

        ## Special checks
        if (m{href="(//gis.cambridgema.gov[^"]+)"}) {
            ## GIS link
            $row{gis} = $1;
            $row{gis} =~ s/&amp;/&/g;
        }
        elsif (/<span id="body_0_content_0_lblAddress">(.*)<\/span/) {
            ## Ttile address
            $row{lblAddress} = $1;
        }
        elsif (m{href="(/Assess/PropertyDatabase/Photos/[^"]+)"}) {
            ## Photo link
            $row{PropertyImageLink} = $1;
            $row{PropertyImageLink} =~ s/&amp;/&/g;
        }
        elsif (/<td.*SA_Code.*>(.*)<\/td>/) {
            ## Entering a subarea
            ## Subareas, such as first floor, have multiple data points
            ## There may be more than one subarea
            $subarea = $1;
            #print "Found subarea code $subarea\n";
        }
        elsif ($subarea eq 'BAS' && /<td.*SA_GrossArea.*>(.*)<\/td>/) {
            ## Only care about the gross area of the first floor
            $row{FirstFloor_GrossArea} = $1;
        }
        elsif (defined $subarea && /<\/tbody>/) {
            $subarea = undef;
            #print "Exiting subarea table\n";
        }
    }

    ## Only add row if data was found
    if (%row) {
        $row{PropId} = $name;
        $rows{$name} = \%row;
    }
    close FILE;
}
