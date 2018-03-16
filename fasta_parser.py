#FASTA Parser
import biopython as bp

# takes in FASTA file or FASTA file segment as input

#Start at certain char and end at certain char to get one genome for testing in beginning

def fasta_parser(file) {
    faa = read(file)

    #use biopython str(faa) function to ocnvert to string
    
    return bp.str(faa)
}

#

# output: single string or maybe array(?) of strings?

