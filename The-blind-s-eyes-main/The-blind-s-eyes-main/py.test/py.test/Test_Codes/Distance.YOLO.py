import cv2
from ultralytics import YOLO

KNOWN_REAL_HEIGHT = 20.0
FOCAL_LENGTH = 650.0

def load_ai_model():
    return YOLO("yolov8n.pt")

def connect_camera():
    print("Connecting to the phone stream...")
    url = "http://192.168.1.11:8080/video"
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    return cap

def format_frame(raw_frame):
    return cv2.rotate(raw_frame, cv2.ROTATE_90_CLOCKWISE)

def process_distances(results, annotated_frame):
    for box in results[0].boxes:
        confidence = float(box.conf[0])
        
        if confidence >= 0.50:
            x1, y1, x2, y2 = box.xyxy[0]
            pixel_height = float(y2 - y1)
            
            distance_cm = (KNOWN_REAL_HEIGHT * FOCAL_LENGTH) / pixel_height
            
            text_x = int(x1)
            text_y = int(y1) - 30 
            cv2.putText(annotated_frame, f"Dist: {distance_cm:.1f}cm", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
    return annotated_frame

def main():
    model = load_ai_model()
    cap = connect_camera()
    
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        processed_frame = format_frame(frame)
        frame_count += 1
        
        if frame_count % 4 == 0: 
            results = model(processed_frame, imgsz=320)
            base_annotated_frame = results[0].plot()
            
            final_frame = process_distances(results, base_annotated_frame)
                    
            cv2.imshow("Smart Navigation - Distance Active", final_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('e'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()