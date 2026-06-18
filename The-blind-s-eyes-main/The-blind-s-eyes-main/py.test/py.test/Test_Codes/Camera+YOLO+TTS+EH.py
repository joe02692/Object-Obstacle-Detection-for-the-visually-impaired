import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import colors
import threading
import time
import winsound
import queue
import win32com.client
import pythoncom
import socket

def internet_working():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

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
    model = YOLO("yolov8n.pt")

    cam_url = "http://192.168.1.10:8080/video"
    cap = cv2.VideoCapture(cam_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    q = queue.Queue(maxsize=10)
    threading.Thread(target=tts_worker, args=(q,), daemon=True).start()

    q.put("System initialized. Connecting to camera.")

    frame_count = 0
    last_speak = 0
    last_beep = 0
    retry = 0
    active_objects = []
    
    system_status = "OK"

    while True:
        try:
            ret, frame = cap.read()

            if not ret:
                if not internet_working():
                    if system_status != "WIFI_DOWN":
                        q.put("Error. Wi-Fi connection lost.")
                        system_status = "WIFI_DOWN"
                else:
                    if system_status != "SERVER_DOWN":
                        q.put("Error. Phone server stopped.")
                        system_status = "SERVER_DOWN"

                time.sleep(1)
                retry += 1
                cap.release()

                if retry <= 5:
                    print(f"Connection lost. Retrying... ({retry}/5)")
                    q.put(f"Retrying connection, attempt {retry}")
                    
                    cap = cv2.VideoCapture(cam_url)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    time.sleep(2) 
                    continue
                else:
                    print("No response after 5 retries. System dying automatically.")
                    q.put("Connection completely failed. System shutting down.")
                    time.sleep(4) 
                    break

            if system_status != "OK":
                q.put("Connection restored. Resuming navigation.")
                system_status = "OK"
                retry = 0

            retry = 0  
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame_count += 1

            if frame_count % 4 == 0:
                results = model(frame, imgsz=256, verbose=False)
                active_objects = []
                speech_list = []
                temp_data = []

                for box in results[0].boxes:
                    if float(box.conf[0]) >= 0.45:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        if (y2 - y1) == 0:
                            continue
                        
                        distance = (20.0 * 650.0) / (y2 - y1)
                        cls_id = int(box.cls[0])
                        name = results[0].names[cls_id]
                        temp_data.append((distance, name, cls_id, (x1, y1, x2, y2)))

                temp_data.sort()

                for d, n, cid, coords in temp_data:
                    active_objects.append((d, n, cid, coords))
                    
                    if d < 300:
                        speech_list.append(f"{n} at {int(d)} cm")
                        
                    if d < 35 and (time.time() - last_beep > 1.5):
                        winsound.Beep(2500, 150)
                        last_beep = time.time()

                if speech_list and (time.time() - last_speak > 5):
                    if q.empty():
                        q.put(", ".join(speech_list[:3]))
                        last_speak = time.time()

            for d, n, cid, c in active_objects:
                color = colors(cid, True)
                cv2.rectangle(frame, (c[0], c[1]), (c[2], c[3]), color, 2)
                cv2.putText(frame, n, (c[0], c[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"{int(d)}cm", (c[0], c[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("Smart Navigation System", frame)

            if cv2.waitKey(1) & 0xFF == ord('e'):
                break

        except Exception:
            time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()    