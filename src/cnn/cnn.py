from Bio import SeqIO # FASTA reader
import numpy as np

def find_min_length(fasta_sequences):
    seq_lengths = []

    for fasta in fasta_sequences:
        name, sequence = fasta.id, str(fasta.seq)
        seq_lengths.append(len(sequence))

    return min(seq_lengths)

def one_hot_encode(seq):
    # https://en.wikipedia.org/wiki/FASTA_format#Sequence_representation
    ltrdict = {'a':[1,0,0,0],'c':[0,1,0,0],'g':[0,0,1,0],'t':[0,0,0,1], 'b':[0,0,0,0], 'v':[0,0,0,0], 'n':[0,0,0,0], 'd':[0,0,0,0], 'm':[0,0,0,0], 'h':[0,0,0,0], 'w':[0,0,0,0], 'y':[0,0,0,0], 's':[0,0,0,0], 'r':[0,0,0,0], 'k':[0,0,0,0]}
    return [ltrdict[x] for x in seq]

def get_data(fasta_sequences):
    min_len = 9083 # in the dengue_fasta
    sequences = []
    for i, fasta in enumerate(fasta_sequences):
        if i == 300:
            break
        name, sequence = fasta.id, str(fasta.seq)
        one_hot_sequence = one_hot_encode(sequence.lower())
        if (len(one_hot_sequence) >= min_len):
            one_hot_sequence = one_hot_sequence[0: (min_len-1)]
        sequences.append(one_hot_sequence)
    return np.asarray(sequences)

from torch.utils.data import Dataset, DataLoader

class VirLabDataset(Dataset):
    """ VirLabDataset dataset."""

    # Initialize your data, download, etc.
    def __init__(self, data, labels):
        self.len = data.shape[0]
        self.x_data = data
        self.y_data = labels

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.len


import torch.nn as nn
import torch.optim as optim

class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.mp = nn.MaxPool2d(2)
        self.fc = nn.Linear(320, 10)

    def forward(self, x):
        in_size = x.size(0)
        x = F.relu(self.mp(self.conv1(x)))
        x = F.relu(self.mp(self.conv2(x)))
        x = x.view(in_size, -1)  # flatten the tensor
        x = self.fc(x)
        return F.log_softmax(x)

def main():
    file = "/Users/alevenberg/research/VirLab/src/cnn/genomes/aedes/dengue.fasta"
    filetype = "fasta"
    aedes_fasta_sequences = list(SeqIO.parse(file, filetype))

    aedes_data = get_data(aedes_fasta_sequences)
    aedes_labels = np.ones(300)

    file = "/Users/alevenberg/research/VirLab/src/cnn/genomes/culex/japanese-encephalitis.fasta"
    filetype = "fasta"
    culex_fasta_sequences = list(SeqIO.parse(file, filetype))

    min_len = find_min_length(culex_fasta_sequences)
    culex_data = get_data(culex_fasta_sequences)
    culex_labels = np.zeros(300)

    data = np.concatenate((aedes_data, culex_data))
    labels = np.concatenate((aedes_labels, culex_labels))

    dataset = VirLabDataset(data, labels)
    train_loader = DataLoader(dataset=dataset,
                              batch_size=30,
                              shuffle=True,
                              num_workers=2)

    model = Net()

main()
