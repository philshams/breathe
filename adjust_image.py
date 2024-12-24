import numpy as np
from PIL import Image

# Load the image
image = Image.open("static/dusky3.jpg")

# Convert to NumPy array
image_np = np.array(image)

# Modify the array (e.g., invert colors)
bright_idx = np.sum(image_np, axis = 2) > 140

# Get the shape of the original array
rows, cols = image_np[:,:,0].shape

# Create an array with the y-index values
y_index_array = np.tile(np.arange(rows), (cols, 1)).T
x_index_array = np.tile(np.arange(cols), (rows, 1))
low_index = y_index_array < 900
not_middle_index = (x_index_array < 1200) + (x_index_array > 2000) + (y_index_array < 600)

image_np[bright_idx * low_index * not_middle_index] = 100

# Convert back to PIL Image
modified_image = Image.fromarray(image_np)

# Save the image
modified_image.save("modified_image.jpg")