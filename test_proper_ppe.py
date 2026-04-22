import cv2
import time
import os
import sys
from datetime import datetime
from ultralytics import YOLO

def main():
    # Make sure 'proper ppe' directory exists
    output_dir = 'proper ppe'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Loading model...")
    model = YOLO('model/best.pt')

    PERSON_CLASS = 0
    REQUIRED_GEAR_CLASSES = [1, 2, 4, 10] # boots, gloves, helmet, vest
    EXPLICIT_VIOLATION_CLASSES = [5, 6, 7, 8, 9] # no_boots, no_gloves, no_goggles, no_helmet, etc.
    
    # Tracking variables
    proper_ppe_count = 0
    
    # Cooldown variables
    frame_count = 0
    last_save_frame = -9999
    cooldown_seconds = 2 # Wait 2 seconds before taking another valid screenshot

    if len(sys.argv) < 2:
        print("Usage: python test_proper_ppe.py <path_to_video.mp4>")
        return
        
    video_path = sys.argv[1]
    print(f"Opening video file: {video_path}...")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return

    print("Starting inference loop. Press 'q' to quit.")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps == 0:
        fps = 30.0 # fallback
    cooldown_frames = int(fps * cooldown_seconds)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video ended or failed to grab frame.")
            break
            
        frame_count += 1

        # Run inference
        results = model(frame, conf=0.5, verbose=False)
        
        # Get detected classes from this frame
        detected_classes = set()
        for r in results:
            for box in r.boxes:
                detected_classes.add(int(box.cls[0]))

        # Condition for Proper PPE: 
        # 1. Person is detected
        # 2. All required gear classes (helmet, boots, gloves, vest) are explicitly detected
        # 3. No violation classes are detected
        has_person = PERSON_CLASS in detected_classes
        has_all_required = all(gear in detected_classes for gear in REQUIRED_GEAR_CLASSES)
        has_no_violations = not any(violation in detected_classes for violation in EXPLICIT_VIOLATION_CLASSES)

        is_proper_ppe = has_person and has_all_required and has_no_violations
        
        # Plot standard detections from YOLO
        annotated_frame = results[0].plot()

        if is_proper_ppe:
            # Draw green success text
            cv2.putText(annotated_frame, "STATUS: Proper PPE Verified!", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Save image if cooldown (in video frames) has passed
            if (frame_count - last_save_frame) > cooldown_frames:
                proper_ppe_count += 1
                last_save_frame = frame_count
                
                # Save the image
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(output_dir, f"proper_ppe_{proper_ppe_count}_{timestamp_str}.jpg")
                cv2.imwrite(filename, annotated_frame)
                print(f"Proper PPE detected! Saved screenshot to {filename}")

        # Always draw the Total Captures Count on the screen
        cv2.putText(annotated_frame, f"Proper PPE Snapshots: {proper_ppe_count}", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Display the result
        cv2.imshow("Proper PPE Capture Tool", annotated_frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
