#!/bin/bash

usage(){
echo "
Written by Brian Bushnell
Last modified August 12, 2019

Description:  Cuts out features defined by a gff file, and writes them
to a new fasta.  Features are output in their sense strand.

Usage:  cutgff.sh in=<fna file> gff=<gff file> out=<fna file>

Peak-calling parameters:
in=<file>           Input FNA (fasta) file.
gff=<file>          Input GFF file (optional).
out=<file>          Output FNA file.
types=CDS           Types of features to cut.
invert=false        Invert selection.
attributes=         A comma-delimited list of strings.  If present, one of
                    these strings must be in the gff line attributes.
bannedattributes=   A comma-delimited list of banned strings.
banpartial=t        Ignore lines with 'partial=true' in attributes.
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

z="-Xmx200m"
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

gff() {
	local CMD="java $EA $EOOM $z -cp $CP gff.CutGff $@"
#	echo $CMD >&2
	eval $CMD
}

gff "$@"
