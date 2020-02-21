import torch
from torch.utils import data
 
CATEGORIES = ["Aedes", "Culex"] # Aedes = 0 and Culex = 1

class dataset(data.Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, path, list_IDs, labels):
        """
        Initialization
        Args:
            path (string): path to directory with test and train subdirectories that hold fasta files
        """
        for i in range(len(CATEGORIES)):
            category = CATEGORIES[i]
            path = os.path.join(path, "Test_" + category)
            files = glob.glob(path + '/**/*.fasta', recursive=True)
            for file in files:
                # pase fasta file
            # for dirName, subdirList, fileList in os.walk(path):
            #     print(dirName)
            #     print(subdirList)
            #     print(fileList)
            a = np.empty(len(data))
            np.fill(i)
            print(files)
        'Initialization'
        self.labels = labels
        self.list_IDs = list_IDs

  def __len__(self):
        'Denotes the total number of samples'
        return len(self.list_IDs)

  def __getitem__(self, index):
        'Generates one sample of data'
        # Select sample
        ID = self.list_IDs[index]

        # Load data and get label
        X = torch.load('data/' + ID + '.pt')
        y = self.labels[ID]

        return X, y