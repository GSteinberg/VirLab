#!/bin/bash

usage(){
echo "
Written by Brian Bushnell
Last modified August 8, 2019

Description:  Writes a shell script to download one genome assembly
and gff per prokaryotic genus, from ncbi.

Usage:  fetchproks.sh <url> <outfile>

Examples:
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/bacteria/ bacteria.sh
fetchproks.sh ftp://ftp.ncbi.nih.gov/genomes/refseq/archaea/ archaea.sh

Processing parameters:
None yet!

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

z="-Xmx1g"
z2="-Xms1g"
set=0

if [ -z "$1" ] || [[ $1 == -h ]] || [[ $1 == --help ]]; then
	usage
	exit
fi

calcXmx () {
	source "$DIR""/calcmem.sh"
	setEnvironment
	parseXmx "$@"
}
calcXmx "$@"

fetchproks() {
	local CMD="java $EA $EOOM $z -cp $CP prok.FetchProks $@"
	echo $CMD >&2
	eval $CMD
}

fetchproks "$@"
