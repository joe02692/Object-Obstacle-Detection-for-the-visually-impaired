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

# ---------------- INTERNET CHECK ----------------
def internet_working():
    try:
        # Pinging Google's DNS to check if the network is alive
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

# ---------------- TEXT TO SPEECH ----------------
def tts_worker(q):
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    while True:
        msg = q.get()
        if msg:
            speaker.Speak(msg)
        q.task_done()

# ---------------- MAIN ----------------
def main():
    model = YOLO("yolov8n.pt")

    # Reverted to 0 to match your very first code (Local Webcam/USB)
    # If using WiFi DroidCam, replace 0 with "http://192.168.1.4:4747/mjpegfeed"
    cam_source = 0 
    cap = cv2.VideoCapture(cam_source)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    q = queue.Queue(maxsize=1)
    threading.Thread(target=tts_worker, args=(q,), daemon=True).start()

    frame_count = 0
    last_speak = 0
    last_beep = 0
    retry = 0
    active_objects = []

    while True:
        try:
            ret, frame = cap.read()

            # ---------------- ERROR HANDLING ----------------
            if not ret:
                print("Frame lost - checking connection...")

                # Logic to determine if it's a WiFi issue or a Hardware issue
                if not internet_working():
                    if q.empty():
                        q.put_nowait("WiFi connection is lost")
                else:
                    if q.empty():
                        q.put_nowait("Camera is disconnected")

                time.sleep(2)
                retry += 1
                cap.release()

                if retry < 5:
                    cap = cv2.VideoCapture(cam_source)
                    continue
                else:
                    if q.empty():
                        q.put_nowait("System stopped due to camera failure")
                    break

            retry = 0  # Reset retry counter on successful read
            
            # Rotate frame to match your original orientation
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame_count += 1

            # ---------------- YOLO DETECTION ----------------
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

                        # Distance calculation logic from original code
                        distance = (20.0 * 650.0) / (y2 - y1)
                        cls_id = int(box.cls[0])
                        name = results[0].names[cls_id]

                        temp_data.append((distance, name, cls_id, (x1, y1, x2, y2)))

                temp_data.sort()

                for d, n, cid, coords in temp_data:
                    active_objects.append((d, n, cid, coords))

                    if d < 300:
                        speech_list.append(f"{n} at {int(d)} centimeters")

                    if d < 35 and (time.time() - last_beep > 1.5):
                        winsound.Beep(2500, 150)
                        last_beep = time.time()

                if speech_list and (time.time() - last_speak > 5):
                    if q.empty():
                        q.put_nowait(", ".join(speech_list[:3]))
                        last_speak = time.time()

            # ---------------- DRAWING ----------------
            for d, n, cid, c in active_objects:
                color = colors(cid, True)
                cv2.rectangle(frame, (c[0], c[1]), (c[2], c[3]), color, 2)
                cv2.putText(frame, n, (c[0], c[1] - 15), 0, 0.6, color, 2)
                cv2.putText(frame, f"{int(d)}cm", (c[0], c[1] - 40), 0, 0.6, (0, 0, 255), 2)

            cv2.imshow("Smart Navigation System", frame)

            if cv2.waitKey(1) & 0xFF == ord('e'):
                break

        except Exception as e:
            print(f"Unexpected Error: {e}")
            time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()