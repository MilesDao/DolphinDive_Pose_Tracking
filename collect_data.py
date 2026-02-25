import cv2
import os
import time

# Create directories for the dataset
dataset_dir = "flappy_pose_dataset/images/train"
os.makedirs(dataset_dir, exist_ok=True)

# Camera settings matching your game.py resolution
wCam, hCam = 640, 360
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

print("--- Flappy Bird Pose Data Collection ---")
print("Press 's' to save a single frame.")
print("Press 'r' to toggle continuous recording (saves 1 frame every 0.2 seconds).")
print("Press 'q' to quit.")

recording = False
last_save_time = 0
save_interval = 0.2  # seconds between frames when recording

# Start numbering based on how many files already exist
existing_files = [f for f in os.listdir(dataset_dir) if f.endswith(".jpg")]
frame_count = len(existing_files)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to read from webcam.")
        break
        
    img = cv2.flip(img, 1)
    
    display_img = img.copy()
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('r'):
        recording = not recording
        print(f"Recording Mode: {'ON' if recording else 'OFF'}")
    elif key == ord('s'):
        filename = os.path.join(dataset_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(filename, img)
        print(f"Saved: {filename}")
        frame_count += 1
        
    if recording:
        current_time = time.time()
        if current_time - last_save_time >= save_interval:
            filename = os.path.join(dataset_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(filename, img)
            print(f"Auto-saved: {filename}")
            frame_count += 1
            last_save_time = current_time
            
        cv2.putText(display_img, "RECORDING (Press 'r' to stop)", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(display_img, "PAUSED (Press 'r' to start, 's' to save one)", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(display_img, f"Images saved: {frame_count}", (20, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Data Collection", display_img)

cap.release()
cv2.destroyAllWindows()
print(f"\nData collection finished! {frame_count} total images in '{dataset_dir}'.")
print("Next step: Upload this folder to Roboflow or CVAT to annotate exactly 17 keypoints per person.")
