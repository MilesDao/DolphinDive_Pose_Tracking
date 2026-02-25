import os
import cv2
import yaml
from ultralytics import YOLO

def auto_annotate():
    # Directories
    dataset_root = "flappy_pose_dataset"
    images_dir = os.path.join(dataset_root, "images", "train")
    labels_dir = os.path.join(dataset_root, "labels", "train")
    
    # Create labels directory if it doesn't exist
    os.makedirs(labels_dir, exist_ok=True)
    
    # Load the pretrained model to generate initial annotations
    print("Loading YOLOv8n-pose model...")
    try:
        model = YOLO("yolov8n-pose.pt")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Get list of images
    if not os.path.exists(images_dir):
        print(f"Images directory not found: {images_dir}")
        print("Please run collect_data.py first to gather images.")
        return
        
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    if not image_files:
        print(f"No images found in {images_dir}")
        return
        
    print(f"Found {len(image_files)} images. Starting auto-annotation...")
    
    annotated_count = 0
    for img_file in image_files:
        img_path = os.path.join(images_dir, img_file)
        # Create corresponding label filename (.txt instead of .jpg)
        label_file = os.path.splitext(img_file)[0] + ".txt"
        label_path = os.path.join(labels_dir, label_file)
        
        # Run inference
        results = model(img_path, verbose=False)
        
        # Open label file for writing
        with open(label_path, 'w') as f:
            for r in results:
                boxes = r.boxes
                keypoints = r.keypoints
                
                # Check if a person is detected
                if boxes is not None and len(boxes) > 0 and keypoints is not None and len(keypoints) > 0:
                    for i in range(len(boxes)):
                        # Only process class 0 (person)
                        if int(boxes.cls[i].item()) != 0:
                            continue
                            
                        # Get normalized bounding box coordinates (x_center, y_center, width, height)
                        # We need normalized coordinates for YOLO format
                        x_c, y_c, w, h = boxes.xywhn[i].tolist()
                        
                        # Start line with class index and bbox coordinates
                        line = f"0 {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}"
                        
                        # Process 17 keypoints
                        kpts = keypoints.data[i].tolist()
                        # Ensure we get normalized coordinates for keypoints too
                        # YOLO format expects keypoints normalized between 0-1
                        img_h, img_w = r.orig_shape
                        
                        for kpt in kpts:
                            px, py, conf = kpt
                            # Normalize keypoint coordinates
                            norm_x = px / img_w if img_w > 0 else 0
                            norm_y = py / img_h if img_h > 0 else 0
                            
                            # Determine visibility
                            # 2 = labeled and visible
                            # 1 = labeled but not visible (occluded)
                            # 0 = not labeled (outside image)
                            if conf > 0.5:
                                vis = 2
                            elif conf > 0.1:
                                vis = 1
                            else:
                                vis = 0
                                norm_x = 0.0
                                norm_y = 0.0
                                
                            line += f" {norm_x:.6f} {norm_y:.6f} {vis}"
                            
                        # Write to file
                        f.write(line + "\n")
                        
        annotated_count += 1
        if annotated_count % 10 == 0:
            print(f"Annotated {annotated_count}/{len(image_files)} images...")
            
    print(f"Successfully auto-annotated {annotated_count} images!")
    print(f"Labels saved in: {labels_dir}")
    
    # Create dataset.yaml automatically
    yaml_path = os.path.join(dataset_root, "dataset.yaml")
    yaml_content = {
        'path': os.path.abspath(dataset_root),
        'train': 'images/train',
        'val': 'images/train',  # Using train for val since it's a small custom dataset
        'names': {0: 'person'},
        'kpt_shape': [17, 3]
    }
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, sort_keys=False)
        
    print(f"Created dataset config at: {yaml_path}")
    print("\nTo train the model directly, run:")
    print(f"yolo pose train data={yaml_path} model=yolov8n-pose.pt epochs=50 imgsz=640 device=0 plots=True")

if __name__ == "__main__":
    auto_annotate()
