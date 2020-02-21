import torch 
import torchvision 
import torchvision.transforms as transforms 
# import dask.dataframe as dd
from keras.utils import to_categorical

TRANSFORM = transforms.Compose([transforms.ToTensor()])
DATA_PATH = './data'

# For one-hot encoding
bmap = {"A":0, "C":1, "G":2, "T":3}
def one_hot(b):
    t = [[0,0,0,0]]
    i = bmap[b]
    t[0][i] = 1
    return t

seq
# seq_t = Variable(torch.FloatTensor([one_hot(c) for c in seq])).cuda()

print("Loading CSV...")
# test = dd.read_csv("../results/training_sig_k_mers.csv", encoding = "UTF-8")
# train = dd.read_csv("../results/testing_sig_k_mers.csv", encoding = "UTF-8")

# print("Converting to Tensor...")
# test_tensor = torch.tensor(test)
# train_tensor = torch.tensor(train)
# # # Dataset
# # train_dataset = torchvision.datasets.MNIST(root=DATA_PATH,
# #                                            train=True,
# #                                            transform=TRANSFORM,
# #                                            download=True)

# # test_dataset = torchvision.datasets.MNIST(root=DATA_PATH,
# #                                           train=False,
#                                           transform=TRANSFORM)

def main():
	# analyze_range(K_MIN, K_MAX, DATASET1, DATASET2)

main()