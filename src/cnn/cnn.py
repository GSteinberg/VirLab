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
        sequences.append(np.expand_dims(one_hot_sequence, axis=0))
    # print((np.asarray(sequences, dtype=np.double)).dtype)
    return np.asarray(sequences, dtype=np.double)

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
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F



class Net(nn.Module):

    def __init__(self):
        KERNEL_SIZE = 4
        LAYER_ONE_CHANNELS = 2
        LAYER_TWO_CHANNELS = 4
        super(Net, self).__init__()
        # Unsure what happens with kernel_size != 1
        self.conv1 = nn.Conv2d(in_channels = 1, out_channels = 10, kernel_size=1, padding=0)
        self.conv2 = nn.Conv2d(in_channels = 10, out_channels = 20, kernel_size=1)
        self.mp = nn.MaxPool2d(2)
        self.fc = nn.Linear(45400, 10)

    def forward(self, x):
        in_size = x.size(0)
        x = F.relu(self.mp(self.conv1(x)))
        x = F.relu(self.mp(self.conv2(x)))
        x = x.view(in_size, -1)  # flatten the tensor
        x = self.fc(x)
        return F.log_softmax(x)


def train(model, train_loader, epoch):
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = Variable(data), Variable(target)
        optimizer.zero_grad()
        output = model(data)
        target = target.long()
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % 10 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))


def test(model):
    model.eval()
    test_loss = 0
    correct = 0
    for data, target in test_loader:
        data, target = Variable(data, volatile=True), Variable(target)
        output = model(data)
        # sum up batch loss
        test_loss += F.nll_loss(output, target, size_average=False).data
        # get the index of the max log-probability
        pred = output.data.max(1, keepdim=True)[1]
        correct += pred.eq(target.data.view_as(pred)).cpu().sum()

    test_loss /= len(test_loader.dataset)
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

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

    # 300 batches, 1 channel, H=9082, W=4
    print("Data size: ", culex_data.shape) # (300, 1, 9082, 4)
    print("Data size: ", aedes_data.shape) # (300, 1, 9082, 4)
    print("Dataset size: ", len(dataset)) # 600 - 300 Aedes and 300 Culex
    model = Net()
    model = model.double()
    for epoch in range(1, 10):
        train(model, train_loader, epoch)
    #     test(model)

    # https://github.com/hunkim/PyTorchZeroToAll/blob/master/10_1_cnn_mnist.py
    # https://hanqingguo.github.io/CNN1
    # https://towardsdatascience.com/pytorch-layer-dimensions-what-sizes-should-they-be-and-why-4265a41e01fd
    # http://cs231n.github.io/convolutional-networks/
main()
