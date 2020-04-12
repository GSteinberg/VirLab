from Bio import SeqIO # FASTA reader
import numpy as np
from data import get_data

# Hyper parameters
total_epochs = 10
batch_size = 30
learning_rate = 0.1

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
import torch

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
        self.fc = nn.Linear(45300, 10)

    def forward(self, x):
        in_size = x.size(0)
        x = F.relu(self.mp(self.conv1(x)))
        x = F.relu(self.mp(self.conv2(x)))
        x = x.view(in_size, -1)  # flatten the tensor
        x = self.fc(x)
        return F.log_softmax(x)


def train(model, train_loader, epoch):
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.5)
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


def test(model, test_loader, epoch):
    model.eval()
    test_loss = 0
    correct = 0
    for data, target in test_loader:
        data, target = Variable(data, volatile=True), Variable(target)
        output = model(data)
        # sum up batch loss
        target = target.long()
        test_loss += F.nll_loss(output, target, size_average=False).data
        # get the index of the max log-probability
        pred = output.data.max(1, keepdim=True)[1]
        correct += pred.eq(target.data.view_as(pred)).cpu().sum()

    test_loss /= len(test_loader.dataset)
    print('\nTest Epoch: {} Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        epoch, test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

def main():
    print ("Getting data...")
    clean_data = get_data()

    aedes_data = clean_data["aedes"]
    aedes_size = len(aedes_data)
    aedes_labels = np.ones(aedes_size)

    culex_data = clean_data["culex"]
    culex_size = len(culex_data)
    culex_labels = np.zeros(culex_size)

    data = np.concatenate((aedes_data, culex_data))
    labels = np.concatenate((aedes_labels, culex_labels))

    full_dataset = VirLabDataset(data, labels)
    train_size = int(0.8 * len(full_dataset))
    test_size = len(full_dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(full_dataset, [train_size, test_size])
    train_loader = DataLoader(dataset=train_dataset,
                              batch_size=batch_size,
                              shuffle=True,
                              num_workers=2)

    test_loader = DataLoader(dataset=test_dataset,
                              batch_size=batch_size,
                              shuffle=True)

    # 300 batches, 1 channel, H=9082, W=4
    print("Culex Data size: ", culex_data.shape) # (300, 1, 9082, 4)
    print("Aedes Data size: ", aedes_data.shape) # (300, 1, 9082, 4)
    print("Dataset size: ", len(full_dataset)) # 600 - 300 Aedes and 300 Culex

    print("Training size: ", len(train_dataset))
    print("Testing size: ", len(test_dataset))

    print ("Running model...")

    model = Net()
    model = model.double()
    for epoch in range(1, total_epochs):
        train(model, train_loader, epoch)
        test(model, test_loader)

main()
