import torch

print("torch version: ", torch.__version__) # torch的版本
print("cuda available: ", torch.cuda.is_available()) # torch能否使用cuda
if torch.cuda.is_available():
    print("cuda version: ",torch.version.cuda)
    print("cudnn version: ",torch.backends.cudnn.version()) # torch使用的cudnn版本
