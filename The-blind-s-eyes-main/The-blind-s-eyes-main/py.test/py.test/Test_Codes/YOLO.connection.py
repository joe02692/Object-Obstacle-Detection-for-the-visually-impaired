import cv2
from ultralytics import YOLO

def load_ai_model():
    return YOLO("yolov8n.pt")

def connect_camera():
    url = "http://192.168.1.15:8080/video"
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    return cap

def format_frame(raw_frame):
    return cv2.rotate(raw_frame, cv2.ROTATE_90_CLOCKWISE)

def main():
    model = load_ai_model()
    cap = connect_camera()

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = format_frame(frame)
        
        frame_count += 1
        
        if frame_count % 4 == 0: 
            results = model(processed_frame)
            annotated_frame = results[0].plot()
                    
            cv2.imshow("Smart Navigation", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('e'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()