import cv2
import face_recognition
from ultralytics import YOLO
from ultralytics.utils.plotting import colors
import threading
import time
import winsound
import queue
import win32com.client
import pythoncom
import socket
import numpy as np

# ==========================================
# 1. HELPER FUNCTIONS & THREADS
# ==========================================
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

def play_alarm():
    # Non-blocking alarm using native winsound
    winsound.PlaySound(r"C:\Users\joeel\OneDrive\Desktop\py.test\Audio\warning_beep.wav",
                        winsound.SND_FILENAME | winsound.SND_ASYNC)

def process_boxes(results, temp_data):
    for box in results[0].boxes:
        if float(box.conf[0]) >= 0.45:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if (y2 - y1) == 0:
                continue
            
            distance = (20.0 * 650.0) / (y2 - y1)
            
            cls_id = int(box.cls[0]) 
            if len(results[0].names) == 1: 
                cls_id += 100
                
            name = results[0].names[int(box.cls[0])]
            temp_data.append((distance, name, cls_id, (x1, y1, x2, y2)))

# ==========================================
# 2. MAIN SYSTEM LOOP
# ==========================================
def main():
    print("Initializing Main System")

    # --- INITIALIZE YOLO MODELS ---
    print("Loading Standard AI...")
    model_base = YOLO("yolov8n.pt")
    print("Loading Custom AI...")
    model_custom = YOLO(r"C:\Users\joeel\py.test\AI Models\YOLO(HNU V1).pt")

    # --- INITIALIZE FACE DATABASE ---
    print("Loading Known Face Database...")
    known_names = ["FILO", "JOE"]
    image_paths = [
        r"C:\Users\joeel\py.test\Face_DB\Filo.jpeg", 
        r"C:\Users\joeel\py.test\Face_DB\Shoukry.jpeg"
    ]
    known_encodings = []

    for path in image_paths:
        try:
            ref_image = face_recognition.load_image_file(path)
            ref_encodings = face_recognition.face_encodings(ref_image)
            if len(ref_encodings) == 1:
                known_encodings.append(ref_encodings[0])
                print(f" Successfully encoded {path}")
            else:
                print(f" Error: Use an image with EXACTLY one face for {path}")
                return
        except FileNotFoundError:
            print(f" Error: Could not find reference file at {path}")
            return

    if not known_encodings:
        print(" No valid reference faces loaded. Cannot continue.")
        return

    # --- CAMERA & NETWORK SETUP ---
    cam_url = "http://10.11.54.2:8080/video"
    cap = cv2.VideoCapture(cam_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    q = queue.Queue(maxsize=10)
    threading.Thread(target=tts_worker, args=(q,), daemon=True).start()
    q.put("System initialized. Connecting to camera.")

    # --- SYSTEM VARIABLES ---
    frame_count = 0
    last_speak = 0
    last_beep = 0
    last_alarm_time = 0
    retry = 0
    system_status = "OK"
    
    # State persistence lists (so boxes don't flicker on skipped frames)
    active_objects = []
    active_faces = [] 

    FACE_THRESHOLD = 0.45 
    ALARM_COOLDOWN = 10 

    print("\n ALL SYSTEMS ONLINE. STARTING NAVIGATION FEED...\n")

    # ==========================================
    # 3. LIVE PROCESSING LOOP
    # ==========================================
    while True:
        try:
            ret, frame = cap.read()

            # --- NETWORK RECONNECT LOGIC ---
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
                    time.sleep(2) 
                    break

            if system_status != "OK":
                q.put("Connection restored. Resuming navigation.")
                system_status = "OK"
                retry = 0

            retry = 0  
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame_count += 1
            
            intruder_detected = False
            
            # --- HEAVY AI PROCESSING (EVERY 4TH FRAME) ---
            if frame_count % 15 == 0:
                
                # ==========================================
                # 1. YOLO PROCESSING (The Lookouts)
                # ==========================================
                results_base = model_base(frame, imgsz=256, verbose=False)
                results_custom = model_custom(frame, imgsz=256, verbose=False)
                
                active_objects = []
                speech_list = []
                temp_data = []
                
                # This flag tells the Face AI to wake up
                person_close_by = False 

                process_boxes(results_base, temp_data)
                process_boxes(results_custom, temp_data)
                temp_data.sort() 

                for d, n, cid, coords in temp_data:
                    active_objects.append((d, n, cid, coords))
                    
                    # Text-to-Speech Warning
                    if d < 300:
                        speech_list.append(f"{n} at {int(d)} cm")
                        
                    # --- THE ACTUAL NOISY ALARM ---
                    # 1. CRITICAL DANGER ZONE (Under 40 cm): Play your loud custom siren
                    if d < 27 and (time.time() - last_beep > 3):
                        winsound.PlaySound(r"C:\Users\joeel\OneDrive\Desktop\py.test\Audio\critical_alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC) 
                        last_beep = time.time()
                        
                    # 2. WARNING ZONE (Under 100 cm): Play your secondary warning sound
                    elif d < 100 and (time.time() - last_beep > 5):
                        winsound.PlaySound(r"C:\Users\joeel\OneDrive\Desktop\py.test\Audio\warning_beep.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                        last_beep = time.time()

                if speech_list and (time.time() - last_speak > 5):
                    if q.empty():
                        q.put(", ".join(speech_list[:3]))
                        last_speak = time.time()


                #==========================================
                # 2. OPTIMIZED FACE RECOGNITION (The Bouncer)
                # ==========================================
                active_faces = [] # Clear old faces
                
                # THE SCALE-DOWN HACK: Shrink the frame to 1/4 size for 400% faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                locations = face_recognition.face_locations(rgb_small)
                encodings = face_recognition.face_encodings(rgb_small, locations)

                for (top, right, bottom, left), face_encoding in zip(locations, encodings):
                    matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=FACE_THRESHOLD)
                    distances = face_recognition.face_distance(known_encodings, face_encoding)
                    
                    best_match_index = np.argmin(distances)
                    
                    person_name = "UNKNOWN PERSON"
                    box_color = (0, 0, 255) 
                    confidence_label = f"({distances[best_match_index]:.2f})"

                    if matches[best_match_index]:
                        person_name = f"{known_names[best_match_index]}"
                        box_color = (0, 255, 0) 
                    else:
                        intruder_detected = True

                    # Scale the coordinates back up by 4 so the boxes draw in the correct place!
                    top *= 2
                    right *= 2
                    bottom *= 2
                    left *= 2

                    # Save face data to draw it outside the loop
                    active_faces.append((left, top, right, bottom, box_color, f"{person_name} {confidence_label}"))


            # --- DRAWING EVERYTHING ON FRAME ---
            # Draw YOLO Objects
            for d, n, cid, c in active_objects:
                color = colors(cid, True)
                cv2.rectangle(frame, (c[0], c[1]), (c[2], c[3]), color, 2)
                cv2.putText(frame, n, (c[0], c[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, f"{int(d)}cm", (c[0], c[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # Draw Faces
            for left, top, right, bottom, box_color, label in active_faces:
                cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)

            # --- INTRUDER ALARM TRIGGER ---
            if intruder_detected:
                current_time = time.time()
                if current_time - last_alarm_time > ALARM_COOLDOWN:
                    play_alarm()
                    last_alarm_time = current_time

            # --- DISPLAY & EXIT ---
            cv2.imshow("Smart Navigation System", frame)

            if cv2.waitKey(1) & 0xFF == ord('e'):
                print("Exit command received. Shutting down system...")
                break

        except Exception as e:
            print(f"Error: {e}") 
            time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()