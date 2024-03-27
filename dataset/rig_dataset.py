import os
import torch
import numpy as np
from torch.utils.data import Dataset

class BVHDataset(Dataset):
    def __init__(self, root_dir):
        """
        Args:
            root_dir (string): Directory with all the subdirectories containing numpy files.
        """
        self.root_dir = root_dir
        self.data_paths = []
        for subdir in os.listdir(root_dir):
            subdir_path = os.path.join(root_dir, subdir)
            if os.path.isdir(subdir_path):
                data_files = [os.path.join(subdir_path, f) for f in os.listdir(subdir_path) if f.endswith('.npy')]
                if data_files:
                    self.data_paths.append(data_files)

    def __len__(self):
        return len(self.data_paths)

    def __getitem__(self, idx):
        data_files = self.data_paths[idx]
        data = {}
        for f in data_files:
            key = os.path.basename(f).split('_')[0]  # Extract key from file name
            data[key] = np.load(f)
        return data

# Example usage:
# dataset = BVHDataset('path/to/root_dir')
# data = dataset[0]  # Get the first data point
