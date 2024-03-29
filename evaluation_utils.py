from train_utils import output_to_class
from sklearn.metrics import f1_score
import torch.nn.functional as F


def get_mean_F1(model, validation_loader):
    """
    returns the mean F1 score for a given dataloader
    """
    model.eval()
    mean_f1 = 0
    for (data, target) in validation_loader:
            output = model(data)
            mean_f1 += f1_score(target.detach().cpu().numpy(), output_to_class(output), average='micro') / len(validation_loader)
            
    return mean_f1


def get_loss(model, validation_loader, device):
    """
    returns loss for a given dataloader
    """
    model.eval()
    loss_epoch = 0
    mean_f1 = 0
    for (data, target) in validation_loader:
        
            data, target = data.to(device), target.to(device)
        
            output = model(data)
            
            loss = F.nll_loss(output, target)
            
            loss_epoch += loss.item() / len(validation_loader)
            mean_f1 += f1_score(target.detach().cpu().numpy(), output_to_class(output), average='micro') / len(validation_loader)
            
    return loss_epoch, mean_f1