"""GENOME CLASS"""

class Genome:

    def __init__( self, v, d, s ):
        self.vector = v
        self.disease = d
        self.sequence = s
        self.trained = False
        self.kmers = {}

    #def populate_dictionary(self):
        # uses logic from sequence to populate kmers