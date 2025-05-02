import os
import shutil
import glob
import argparse

def create_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def read_classes_file(file_path):
    """Read classes from classes.txt file"""
    if not os.path.exists(file_path):
        print(f"Warning: Classes file not found at {file_path}")
        return []
    
    with open(file_path, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    return classes

def write_classes_file(classes, output_path):
    """Write combined classes to a file"""
    with open(output_path, 'w') as f:
        for cls in classes:
            f.write(f"{cls}\n")
    print(f"Wrote combined classes file to {output_path}")

def get_image_files(directory):
    """Get all image files from a directory"""
    image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    image_files = []
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Warning: Images directory not found at {directory}")
        return image_files
    
    # Get all files with image extensions
    for ext in image_exts:
        image_files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
        image_files.extend(glob.glob(os.path.join(directory, f"*{ext.upper()}")))
    
    return image_files

def copy_dataset(dataset_dir, output_dir, prefix=""):
    """Copy dataset files with optional prefix"""
    # Define paths
    images_dir = os.path.join(dataset_dir, "images")
    labels_dir = os.path.join(dataset_dir, "labels")
    
    # Output paths
    output_images_dir = os.path.join(output_dir, "images")
    output_labels_dir = os.path.join(output_dir, "labels")
    
    # Ensure output directories exist
    create_directory(output_images_dir)
    create_directory(output_labels_dir)
    
    # Get all image files
    image_files = get_image_files(images_dir)
    print(f"Found {len(image_files)} images in {images_dir}")
    
    # Copy each image and its corresponding label file
    copied_images = 0
    copied_labels = 0
    
    for img_path in image_files:
        # Get filename and basename
        filename = os.path.basename(img_path)
        basename, ext = os.path.splitext(filename)
        
        # Apply prefix if specified
        new_basename = f"{prefix}{basename}" if prefix else basename
        new_filename = f"{new_basename}{ext}"
        
        # Copy image
        shutil.copy(img_path, os.path.join(output_images_dir, new_filename))
        copied_images += 1
        
        # Look for corresponding label file
        label_path = os.path.join(labels_dir, f"{basename}.txt")
        if os.path.exists(label_path):
            # Copy label file with new name if prefix was applied
            shutil.copy(label_path, os.path.join(output_labels_dir, f"{new_basename}.txt"))
            copied_labels += 1
        else:
            print(f"Warning: No label file found for {filename}")
    
    print(f"Copied {copied_images} images and {copied_labels} label files from {dataset_dir}")
    return copied_images, copied_labels

def merge_classes(dataset1_dir, dataset2_dir, output_dir):
    """Merge classes from two datasets"""
    # Read classes files
    classes1_path = os.path.join(dataset1_dir, "classes.txt")
    classes2_path = os.path.join(dataset2_dir, "classes.txt")
    
    classes1 = read_classes_file(classes1_path)
    classes2 = read_classes_file(classes2_path)
    
    # Check if classes are the same
    if classes1 and classes2:
        if classes1 == classes2:
            print("Class files are identical - using these classes")
            combined_classes = classes1
        else:
            print("Warning: Class files differ between datasets!")
            print(f"Dataset 1 classes: {classes1}")
            print(f"Dataset 2 classes: {classes2}")
            
            # Create a union of classes
            combined_classes = list(dict.fromkeys(classes1 + [c for c in classes2 if c not in classes1]))
            print(f"Using combined classes: {combined_classes}")
            
            # This would require relabeling dataset2 if we're changing class IDs
            print("Note: You may need to manually adjust label files if class IDs have changed")
    elif classes1:
        combined_classes = classes1
        print("Using classes from dataset 1")
    elif classes2:
        combined_classes = classes2
        print("Using classes from dataset 2")
    else:
        combined_classes = []
        print("Warning: No classes file found in either dataset")
    
    # Write combined classes file
    if combined_classes:
        write_classes_file(combined_classes, os.path.join(output_dir, "classes.txt"))
    
    return combined_classes

def combine_datasets(dataset1_dir, dataset2_dir, output_dir, prefix2=""):
    """Combine two YOLO datasets"""
    print(f"\nCombining datasets:")
    print(f"- Dataset 1: {dataset1_dir}")
    print(f"- Dataset 2: {dataset2_dir}")
    print(f"- Output: {output_dir}")
    
    # Create output directory
    create_directory(output_dir)
    
    # Merge classes
    merge_classes(dataset1_dir, dataset2_dir, output_dir)
    
    # Copy files from dataset 1 (no prefix)
    img1, lbl1 = copy_dataset(dataset1_dir, output_dir)
    
    # Copy files from dataset 2 (with optional prefix)
    img2, lbl2 = copy_dataset(dataset2_dir, output_dir, prefix=prefix2)
    
    # Copy notes.json if it exists in either dataset
    for dataset_dir in [dataset1_dir, dataset2_dir]:
        notes_path = os.path.join(dataset_dir, "notes.json")
        if os.path.exists(notes_path):
            shutil.copy(notes_path, os.path.join(output_dir, "notes.json"))
            print(f"Copied notes.json from {dataset_dir}")
            break
    
    print("\nCombination complete:")
    print(f"- Total images: {img1 + img2}")
    print(f"- Total labels: {lbl1 + lbl2}")
    print(f"Combined dataset saved to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine two YOLO datasets")
    parser.add_argument("--dataset1", required=True, help="Path to first dataset directory")
    parser.add_argument("--dataset2", required=True, help="Path to second dataset directory")
    parser.add_argument("--output", required=True, help="Output directory for combined dataset")
    parser.add_argument("--prefix", default="ds2_", help="Prefix to add to second dataset filenames (default: 'ds2_')")
    
    args = parser.parse_args()
    combine_datasets(args.dataset1, args.dataset2, args.output, args.prefix)