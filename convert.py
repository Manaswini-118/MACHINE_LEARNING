import nibabel as nib
import numpy as np
import cv2
import os
import random

# Dataset path
oasis_path = r"C:\Users\manas\OneDrive\Desktop\alzheimer_project\disc1"

base_output = "dataset"
count = 0

for root, dirs, files in os.walk(oasis_path):
    for file in files:
        if file.endswith(".img"):

            img_path = os.path.join(root, file)

            # 🔥 TEMP LABEL (random split for now)
            label = "AD" if random.random() > 0.5 else "Normal"

            try:
                img = nib.load(img_path)
                data = img.get_fdata()

                for i in range(data.shape[2]//2 - 5, data.shape[2]//2 + 5):

                    slice_img = data[:, :, i]

                    slice_img = cv2.normalize(slice_img, None, 0, 255, cv2.NORM_MINMAX)
                    slice_img = np.uint8(slice_img)

                    slice_img = cv2.resize(slice_img, (224, 224))

                    split = "train" if random.random() < 0.8 else "test"

                    save_path = f"{base_output}/{split}/{label}/img_{count}.jpg"

                    cv2.imwrite(save_path, slice_img)
                    count += 1

            except:
                continue

print("✅ DONE: Images created")