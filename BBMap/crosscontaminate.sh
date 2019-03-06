#!/bin/bash

usage(){
echo "
Written by Brian Bushnell
Last modified February 17, 2015

Description:  Generates synthetic cross-contaminated files from clean files.
Intended for use with synthetic reads generated by SynthMDA or RandomReads.

Usage:        crosscontaminate.sh in=<file,file,...> out=<file,file,...>

Input parameters:
in=<file,file,...>  Clean input reads.
innamefile=<file>   A file containing the names of input files, 
                    one name per line.
interleaved=auto    (int) t/f overrides interleaved autodetection.
qin=auto            Input quality offset: 33 (Sanger), 64, or auto.
reads=-1            If positive, quit after processing X reads or pairs.

Processing Parameters:
minsinks=1          Min contamination destinations from one source.
maxsinks=8          Max contamination destinations from one source.
minprob=0.000005    Min allowed contamination rate (geometric distribution).
maxprob=0.025       Max allowed contamination rate.

Output parameters:
out=<file,file,...> Contaminated output reads.
outnamefile=<file>  A file containing the names of output files, 
                    one name per line.
overwrite=t         (ow) Grant permission to overwrite files.
#showspeed=t        (ss) 'f' suppresses display of processing speed.
ziplevel=2          (zl) Compression level; 1 (min) through 9 (max).
threads=auto        (t) Set number of threads to use; default is number of 
                    logical processors.
qout=auto           Output quality offset: 33 (Sanger), 64, or auto.
shuffle=f           Shuffle contents of output files.
shufflethreads=3    Use this many threads for shuffling (uses more memory).

Java Parameters:
-Xmx                This will set Java's memory usage, overriding autodetection.
                    -Xmx20g will specify 20 gigs of RAM, and -Xmx200m will specify 200 megs.
                    The max is typically 85% of physical memory.
-eoom               This flag will cause the process to exit if an
                    out-of-memory exception occurs.  Requires Java 8u92+.
-da                 Disable assertions.

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
EA="-ea"
EOOM=""
set=0

if [ -z "$1" ] || [[ $1 == -h ]] || [[ $1 == --help ]]; then
	usage
	exit
fi

calcXmx () {
	source "$DIR""/calcmem.sh"
	parseXmx "$@"
	if [[ $set == 1 ]]; then
	return
	fi
	freeRam 4000m 42
	z="-Xmx${RAM}m"
}
calcXmx "$@"

crosscontaminate() {
	if [[ $SHIFTER_RUNTIME == 1 ]]; then
		#Ignore NERSC_HOST
		shifter=1
	elif [[ $NERSC_HOST == genepool ]]; then
		module unload oracle-jdk
		module load oracle-jdk/1.8_144_64bit
		module load pigz
	elif [[ $NERSC_HOST == denovo ]]; then
		module unload java
		module load java/1.8.0_144
		module load pigz
	elif [[ $NERSC_HOST == cori ]]; then
		module use /global/common/software/m342/nersc-builds/denovo/Modules/jgi
		module use /global/common/software/m342/nersc-builds/denovo/Modules/usg
		module unload java
		module load java/1.8.0_144
		module load pigz
	fi
	local CMD="java $EA $EOOM $z -cp $CP jgi.CrossContaminate $@"
	echo $CMD >&2
	eval $CMD
}

crosscontaminate "$@"
