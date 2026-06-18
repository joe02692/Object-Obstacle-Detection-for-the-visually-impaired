import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import colors
import threading
import time
import winsound
import queue
import win32com.client 
import pythoncom

def tts_worker(q):
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    
    while True:
        try:
            msg = q.get()
            if msg:
                speaker.Speak(msg)
            q.task_done()
        except:
            time.sleep(0.1)

def main():
    print("\nConnecting to the phone stream...")
    model = YOLO("yolov8n.pt")
    url = "http://192.168.1.10:8080/video"
    cap = cv2.VideoCapture(url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    q = queue.Queue(maxsize=1)
    threading.Thread(target=tts_worker, args=(q,), daemon=True).start()
    
    f_count, last_s, last_b = 0, 0, 0
    active_objs = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("\nFailed to grab frame.")
            break
        
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        f_count += 1
        
        if f_count % 4 == 0:
            results = model(frame, imgsz=256, verbose=False)
            active_objs = []
            speech_list = []
            temp_data = []
            
            for b in results[0].boxes:
                if b.conf[0] >= 0.45:
                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    dist = (20.0 * 650.0) / (y2 - y1)
                    cls_id = int(b.cls[0])
                    name = results[0].names[cls_id]
                    temp_data.append((dist, name, cls_id, (x1, y1, x2, y2)))
            
            temp_data.sort()
            
            for d, n, cid, coords in temp_data:
                active_objs.append((d, n, cid, coords))
                if d < 300: 
                    speech_list.append(f"{n} at {int(d)}")
                
                if d < 35 and (time.time() - last_b > 1.5):
                    winsound.Beep(2500, 150)
                    last_b = time.time()

            if speech_list and (time.time() - last_s > 5):
                if q.empty():
                    full_report = ", ".join(speech_list[:3])
                    q.put_nowait(full_report)
                    last_s = time.time()

        for d, n, cid, c in active_objs:
            obj_color = colors(cid, True)
            
            cv2.rectangle(frame, (c[0], c[1]), (c[2], c[3]), obj_color, 2)
            cv2.putText(frame, f"{int(d)}cm", (c[0], c[1] - 40), 0, 0.6, (0, 0, 255), 2)
            cv2.putText(frame, n, (c[0], c[1] - 15), 0, 0.6, obj_color, 2)

        cv2.imshow("Smart Navigation", frame)
        if cv2.waitKey(1) & 0xFF == ord('e'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()