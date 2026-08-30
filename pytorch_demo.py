from PIL import Image
import numpy as np
import torch


image = Image.open("images/download.jpg")

print("Pillow size:", image.size)
print("Pillow mode:", image.mode)

array = np.array(image)

print("NumPy shape:", array.shape)
tensor = torch.from_numpy(array)

print("Tensor shape:", tensor.shape)
print("Tensor dimensions:", tensor.ndim)