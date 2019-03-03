"""GENOME CLASS"""

class Genome:

	def __init__( self, v, d, s ):
		self.vector = v
		self.disease = d
		self.sequence = s
		self.trained = False
		self.kmers = {}

	def populate_dictionary( self, k_min, k_max ):
		#iterate through each sequence in genomes
		#if substring of length k starting at i is not in kmer_dict,
		#add it as key and initialize value as 1. Else add and increment value
		for k in range(k_min, k_max+1):
			for i in range( len(self.sequence)-(k-1) ):
				read = self.sequence[i:i+k].upper()
				if read in self.kmers:
					self.kmers[read] += 1
				else:
					self.kmers[read] = 1
		for read in self.kmers:
			self.kmers[read] /= ( len(self.sequence) - (len(read)-1) )
			self.kmers[read] *= 100000

	def __str__(self):
		retstr = ">" + self.vector + " " + self.disease + "\n"
		i = 1
		for ch in self.sequence:
			retstr += ch
			if i % 79 == 0:
				retstr += "\n"
			i += 1
		return retstr

