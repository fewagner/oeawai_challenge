import os
import glob
import numpy as np
import re
import scipy.io.wavfile
import torch
import torch.utils.data as data
import torchvision.transforms as transforms
from sklearn.preprocessing import LabelEncoder


"""
    #Pytorch dataset for instruments
    #args:
    #    root: root dir containing an audio directory with wav files.
    #    transform (callable, optional): A function/transform that takes in
    #            a sample and returns a transformed version.
"""

"""
class TestDataset(data.Dataset):


    def __init__(self, root, transform=None):
        assert(isinstance(root, str))

        self.root = root
        self.filenames = glob.glob(os.path.join(root, "audio/*.wav"))           
        self.transform = transform
            
    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, index):
        name = self.filenames[index]
        _, sample = scipy.io.wavfile.read(name) # load audio
        
        no_folders = re.compile('\/').split(name)[-1]
        index = re.compile('\.').split(no_folders)[0]
        if self.transform is not None:
            sample = self.transform(sample)
        return sample, index
"""
    
class TestDataset(data.Dataset):
    """Pytorch dataset for instruments
    args:
        root: root dir containing an audio directory with wav files.
        transform (callable, optional): A function/transform that takes in
                a sample and returns a transformed version.
    """

    def __init__(self, root, transform=None):
        assert(isinstance(root, str))

        self.root = root
        self.filenames = glob.glob(os.path.join(root, "audio/*.wav"))   
        self.filenames.sort(key=self.file_num)
        self.transform = transform
            
    def file_num(self, file_path):
        file_name = re.compile("\/").split(file_path)[-1]
        file_num = re.compile("\.").split(file_name)[0]
        return int(file_num)        
    
    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, index):
        name = self.filenames[index]
        _, sample = scipy.io.wavfile.read(name) # load audio
        
        if self.transform is not None:
            sample = self.transform(sample)
        return sample
