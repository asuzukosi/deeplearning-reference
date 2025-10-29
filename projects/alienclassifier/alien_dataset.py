from torch.utils.data import Dataset
from PIL import Image
import os
import glob

def clean_ben10label_name(label_name: str) -> str:
    """clean the label name"""
    return label_name.replace(' ', '').replace('_', '').replace('ben10', ' ').lower()

class AlienDataset(Dataset):
    def __init__(self, root_dir, 
                transform=None, 
                clean_label_name=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []
        self.classes = []
        self.class_to_idx = {}
        self.idx_to_class = {}
        self.cleaned_classes = []
        self.clean_label_name = clean_label_name
        
        # scan the results directory for subfolders (classes)
        self._load_dataset()

    def _load_dataset(self):
        """load all images from subfolders in the results directory"""
        # get all subdirectories in the results folder
        subdirs = [d for d in os.listdir(self.root_dir) 
                  if os.path.isdir(os.path.join(self.root_dir, d))]
        # sort subdirectories to ensure consistent ordering
        subdirs.sort()
        # create class mappings
        self.cleaned_classes = list(map(self.clean_label_name, subdirs))
        self.classes = subdirs
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.cleaned_classes)}
        self.idx_to_class = {idx: cls_name for cls_name, idx in self.class_to_idx.items()}

        # load all images and their labels
        for class_name in self.classes:
            class_dir = os.path.join(self.root_dir, class_name)
            # get all image files in the class directory
            image_files = glob.glob(os.path.join(class_dir, "*.jpg")) + \
                         glob.glob(os.path.join(class_dir, "*.jpeg")) + \
                         glob.glob(os.path.join(class_dir, "*.png"))
            
            for image_file in image_files:
                self.images.append(image_file)
                self.labels.append(self.class_to_idx[self.clean_label_name(class_name)])
        
        self.classes = self.cleaned_classes
        print(f"Loaded {len(self.images)} images from {len(self.classes)} classes")
        print(f"Classes: {self.classes}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        label = self.labels[idx]
        # load the image
        image = self._load_image(idx)
        if self.transform:
            image = self.transform(image)
        return image, label

    def _load_image(self, index):
        """load image at given index"""
        image_path = self.images[index]
        image = Image.open(image_path).convert('RGB')
        return image
