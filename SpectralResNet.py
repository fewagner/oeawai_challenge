import torch.nn as nn
import torch.nn.functional as F
from math_utils import logMagStft, ffts
import numpy as np
import torch


# CNN resnet architecture
class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != self.expansion*planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, self.expansion*planes, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(self.expansion*planes)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out

class SpectralResNet(nn.Module):
    def __init__(self, device, block, num_blocks, num_classes=10):
        super(SpectralResNet, self).__init__()
        self.in_planes = 64

        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.layer1 = self._make_layer(block, 64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, 128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, 256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(block, 512, num_blocks[3], stride=2)
        self.linear = nn.Linear(32768, num_classes)
        self.device = device

    def _make_layer(self, block, planes, num_blocks, stride):
        strides = [stride] + [1]*(num_blocks-1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion
        return nn.Sequential(*layers)

    def forward(self, x):
        
        n_fft = 510
    
        spectrograms = np.zeros((len(x), n_fft//2+1, int(2*64000/n_fft)+2))
        for index, audio in enumerate(x.cpu().numpy()):
            spectrograms[index] = logMagStft(audio, 16000, n_fft)
        
        x = torch.from_numpy(spectrograms[:, np.newaxis, :, :]).to(self.device).float()
        
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = F.avg_pool2d(out, 4)
        out = out.view(out.size(0), -1)
        
        out = self.linear(out)
        return F.log_softmax(out, dim=1)
    
def SpectralResNet18(device):
    return SpectralResNet(device, BasicBlock, [2,2,2,2])

def SpectralResNet34(device):
    return SpectralResNet(device, BasicBlock, [3,4,6,3])

def SpectralResNet50(device):
    return SpectralResNet(device, Bottleneck, [3,4,6,3])

def SpectralResNet101(device):
    return SpectralResNet(device, Bottleneck, [3,4,23,3])

def SpectralResNet152(device):
    return SpectralResNet(device, Bottleneck, [3,8,36,3])