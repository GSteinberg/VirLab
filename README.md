# VirLab
### Vector identification in metagenomic data using k-mers
- The goal is to find the vector of a disease with an unknown vector by training an SVM on genomes with known vectors.
- Training on complete genomes of diseases vectored by Aedes and Culex mosquitoes
- Testing on simulated reads of complete genomes of diseases vectored by Aedes and Culex mosquitoes

#### Main Files
 1. *fasta_parser.py*
	 - Parses input data and returns an array "genomes" with genome objects populated with vector, disease, and sequence for each genome
 2. *k_mer_creator.py*
	- Populates each genome object with all k-mers for that sequence
	- For every k-mer in all genome objects, it adds a placeholder k-mer (k-mer: 0) for that k-mer all other genomes. So every genome has every k-mer that every other genome has.
	- Split into training & testing sets
	- Make fasta files with testing data for BBMap
	- Simulate reads from test genomes
	- Find significant kmers for testing and training sets and create CSV's with them
 3. *kruskal_wallis.py*
 	- Tests if a kmer can help distinguish two classes by analyzing the difference in the medians
 4. *SVM.py*
 	- CLassification using a Support Vector Machine

#### Instructions
 1. Clone this repository into your home directory
 2. Install BioPython and skikit learn
   - https://biopython.org/
   - https://scikit-learn.org/stable/
   - To install the dependencies, use `pip3 install -r requirements.txt`
 3. For Windows: Install Java in your Linux subsystem for the BBMap script to work  
 4. Run "python k_mer_creator.py" to generate files
 5. Run "SVM.py" to classify

### TODO
 - [ ] Need a way for SVM to return an "i dont know" - distance from the vector
 - [ ] Turning reads into contigs and test on those
 - [ ] Convert some nested for loops to list comprehensions for speed and readability
 - [ ] Adding script for one hot encoding
