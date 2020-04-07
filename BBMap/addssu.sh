#!/bin/bash

usage(){
echo "
Written by Brian Bushnell
Last modified August 22, 2019

Description:  Adds SSU sequence to already-made sketches with TaxIDs.

Usage:           addssu.sh in=a.sketch out=b.sketch ssufile=ssu.fa

Standard parameters:
in=<file>       Input sketch file.
out=<file>      Output sketch file.
ssufile=<file>  A fasta file of SSU sequences.  These should be renamed
                so that they start with tid|# where # is the taxID.

Java Parameters:
-Xmx            This will set Java's memory usage, overriding autodetection.
                -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-da             Disable assertions.

For more detailed information, please read /bbmap/docs/guides/BBSketchGuide.txt.
Please contact Brian Bushnell at bbushnell@lbl.gov if you encounter any problems.
"
}

#This block allows symlinked shellscripts to correctly set classpath.
pushd . > /dev/null
DIR="${BASH_SOURCE[0]}"
while [ -h "$DIR" ]; do
  cd "$(dirname "$DIR")"
  DIR="$(readlink "$(basename "$DIR")")"
done
cd "$(dirname "$DIR")"
DIR="$(pwd)/"
popd > /dev/null

#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/"
CP="$DIR""current/"

z="-Xmx4g"
z2="-Xms4g"
set=0

if [ -z "$1" ] || [[ $1 == -h ]] || [[ $1 == --help ]]; then
	usage
	exit
fi

calcXmx () {
	source "$DIR""/calcmem.sh"
	setEnvironment
	parseXmx "$@"
	if [[ $set == 1 ]]; then
		return
	fi
	#freeRam 3200m 84
	#z="-Xmx${RAM}m"
	#z2="-Xms${RAM}m"
}
calcXmx "$@"

sendsketch() {
	local CMD="java $EA $EOOM $z -cp $CP sketch.AddSSU $@"
	echo $CMD >&2
	eval $CMD
}

sendsketch "$@"
