from Bio import SeqIO

def file_splitter( to_parse ):
	testfile = SeqIO.parse(open(to_parse), "fasta")
	filename = "testfile.faa"
	count = SeqIO.write(testfile, open(filename, "w"), "fasta")
