import os
import cv2
import argparse
from pathlib import Path
from tqdm import tqdm

TARGET_SIZE = 224

def center_crop_resize(image):
    h, w, _ = image.shape
    # Crop to square first
    min_dim = min(h, w)
    top = (h - min_dim) // 2
    left = (w - min_dim) // 2
    cropped = image[top:top+min_dim, left:left+min_dim]
    # Resize to 224x224
    resized = cv2.resize(cropped, (TARGET_SIZE, TARGET_SIZE), interpolation=cv2.INTER_CUBIC)
    return resized

def process_images(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
    all_images = [p for p in input_path.glob("*") if p.suffix.lower() in image_extensions]

    for img_path in tqdm(all_images, desc="Processing images"):
        try:
            image = cv2.imread(str(img_path))
            print("Processing:", str(img_path))
            if image is None:
                print(f"Skipping unreadable file: {img_path.name}")
                continue
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB (optional for CLIP)
            resized = center_crop_resize(image)
            out_path = output_path / img_path.name
            cv2.imwrite(str(out_path), cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))  # Save in BGR
        except Exception as e:
            print(f"Failed to process {img_path.name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resize + crop images for CLIP using OpenCV")
    parser.add_argument("--input", type=str, required=True, help="Input image directory")
    parser.add_argument("--output", type=str, required=True, help="Output image directory")
    args = parser.parse_args()

    process_images(args.input, args.output)