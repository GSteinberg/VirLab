import src.k_mer_creator as k
from pathlib import Path

PERCENT_TRAIN = 0.7
MIN_GEN_LEN = 76
MIN_SIG_KMERS = 2
K_MIN = 4
K_MAX = 4
DATASET1_PATH = str(Path("genomes/Test_Aedes"))
DATASET2_PATH = str(Path("genomes/Test_Culex"))

PATH = ""


def main():
    k.analyze_range(K_MIN, K_MAX, DATASET1_PATH, DATASET2_PATH)
main()
