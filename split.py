import os
import shutil
import random

base_dir = "dataset"
train_dir = "dataset_split/train"
test_dir = "dataset_split/test"

classes = os.listdir(base_dir)

for cls in classes:
    os.makedirs(os.path.join(train_dir, cls), exist_ok=True)
    os.makedirs(os.path.join(test_dir, cls), exist_ok=True)

    images = os.listdir(os.path.join(base_dir, cls))

    for img in images:
        src = os.path.join(base_dir, cls, img)

        if random.random() < 0.8:
            dst = os.path.join(train_dir, cls, img)
        else:
            dst = os.path.join(test_dir, cls, img)

        shutil.copy(src, dst)

print("✅ Dataset split done")