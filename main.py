import cv2
import time
import os
from datetime import datetime
from ultralytics import YOLO

def main():
    # Make sure violations directory exists
    if not os.path.exists('violations'):
        os.makedirs('violations')

    print("Loading model...")
    model = YOLO('model/best.pt')

    # The new model already has the correct names internally:
    # {0: 'Person', 1: 'boots', 2: 'gloves', 3: 'goggles', 4: 'helmet', 5: 'no_boots', ...}
    
    PERSON_CLASS = 0
    REQUIRED_GEAR_CLASSES = [1, 2, 4, 10] # boots, gloves, helmet, vest

    # Tracking variables
    violation_count = 0
    last_violation_time = 0
    cooldown_seconds = 5 # Wait 5 seconds before logging another violation image

    print("Opening webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting inference loop. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Run inference
        results = model(frame, conf=0.5, verbose=False)
        
        # Get detected classes from this frame
        detected_classes = set()
        for r in results:
            for box in r.boxes:
                # Add the class id to our set of detected items
                detected_classes.add(int(box.cls[0]))

        violation_triggered = False
        missing_gears = []

        EXPLICIT_VIOLATION_MAP = {
            5: 'boots',
            6: 'gloves',
            7: 'goggles',
            8: 'helmet',
            9: 'PPE (none detected)'
        }

        # Logic: We now rely EXCLUSIVELY on the model explicitly telling us  
        # that a required gear is missing via its negative classes.
        # This prevents false positives when body parts are just out of frame!
        for explicit_class, gear_name in EXPLICIT_VIOLATION_MAP.items():
            if explicit_class in detected_classes:
                violation_triggered = True
                if gear_name not in missing_gears:
                    missing_gears.append(gear_name)
        
        # Special check for vest since there is no 'no_vest' class
        # If a person (0) is detected but no vest (10) is detected anywhere in the frame
        if 0 in detected_classes and 10 not in detected_classes:
            violation_triggered = True
            if 'vest' not in missing_gears:
                missing_gears.append('vest')
        
        # Plot standard detections from YOLO
        annotated_frame = results[0].plot()

        # Handle violations
        if violation_triggered:
            current_time = time.time()
            
            # Format the alert message
            alert_text = f"ALERT: Missing {', '.join(missing_gears)}!"
            cv2.putText(annotated_frame, alert_text, (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Save image and increment count if cooldown has passed
            if current_time - last_violation_time > cooldown_seconds:
                violation_count += 1
                last_violation_time = current_time
                
                # Save the image
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"violations/violation_{violation_count}_{timestamp_str}.jpg"
                cv2.imwrite(filename, annotated_frame)
                print(f"Violation recorded! Saved to {filename}")

        # Always draw the Total Violations Count on the screen
        cv2.putText(annotated_frame, f"Total Violations: {violation_count}", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

        # Display the result
        cv2.imshow("PPE Detection System", annotated_frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
