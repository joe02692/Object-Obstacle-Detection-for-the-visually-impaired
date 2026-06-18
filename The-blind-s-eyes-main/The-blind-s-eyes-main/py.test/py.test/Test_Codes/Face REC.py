import cv2
import face_recognition
from playsound import playsound
import threading
import time
import numpy as np  # Necessary for finding the best match

# -------------------------------
# ALARM (THREAD SAFE)
# -------------------------------
# This function is designed to be called from a new thread so the video
# feed doesn't freeze when the alarm sound is playing.
def play_alarm():
    # Force a stable playsound version to prevent Windows file locking bugs
    playsound(r"C:\Users\joeel\Downloads\Blind\ai2\warning_beep.wav", block=False) # Non-blocking to let the video continue

# -------------------------------
# PHASE 1: LOAD & ENCODE KNOWN FACES (THE DATABASE)
# -------------------------------
# To add a person to the trusted list, you just need to:
# 1. Add their name to the list below.
# 2. Add the path to their reference image in the list below.

# Make sure you have saved face_1.jpg and face_2.jpg in D:\pic\
known_names = ["FILO", "JOE"]
image_paths = [r"C:\Users\joeel\Downloads\WhatsApp Unknown 2026-05-03 at 11.48.32 AM\Filo.jpeg", 
               r"C:\Users\joeel\Downloads\WhatsApp Unknown 2026-05-03 at 11.48.32 AM\Shoukry.jpeg"]

print("Initializing known face database...")
known_encodings = []

# Loop through each path, load the image, and compute its mathematical encoding
for path in image_paths:
    try:
        ref_image = face_recognition.load_image_file(path)
        ref_encodings = face_recognition.face_encodings(ref_image)
        
        # Security check: Make sure each reference photo only has one clear face
        if len(ref_encodings) == 1:
            known_encodings.append(ref_encodings[0])
            print(f" Successfully encoded {path}")
        else:
            print(f" Error: Use an image with EXACTLY one face for {path}")
            exit()
    except FileNotFoundError:
        print(f" Error: Could not find reference file at {path}")
        exit()

if not known_encodings:
    print(" No valid reference faces loaded. Cannot continue.")
    exit()

print("Initialization complete! Security system online.")

# -------------------------------
# SETTINGS
# -------------------------------
# A lower THRESHOLD is stricter (e.g., 0.28). Higher is more relaxed (0.6).
# For a security system, a low number like 0.28 or 0.3 is optimal to prevent false "You" matches.
THRESHOLD = 0.30 
ALARM_COOLDOWN = 10   # seconds between alarms

# Create a queue to manage the alarm thread so it doesn't double-play
alarm_queue = []

# -------------------------------
# PHASE 2: CAMERA & LIVE LOOP
# -------------------------------
cap = cv2.VideoCapture(0) # '0' is your PC's default webcam

if not cap.isOpened():
    print(" Error: Could not open the camera feed.")
    exit()

last_alarm_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # face_recognition works best on RGB images, OpenCV defaults to BGR
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find the locations of all faces in the current frame and compute their encodings
    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)

    # Flag to keep track if we found a face that isn't in our list
    intruder_detected = False

    # Process every face found in the current frame
    for (top, right, bottom, left), face_encoding in zip(locations, encodings):

        # First, check this face against all known faces in one step
        # compare_faces returns a simple list of True/False matches
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=THRESHOLD)
        
        # Second, get the raw distance (math difference) against all known faces
        distances = face_recognition.face_distance(known_encodings, face_encoding)

        # Optimization trick: Find the index of the face that is mathematically closest
        # This tells us whose "face" it resembles the most
        best_match_index = np.argmin(distances)
        
        person_name = "UNKNOWN PERSON"
        box_color = (0, 0, 255) # Red for danger
        confidence_label = f"({distances[best_match_index]:.2f})"

        # Logic for "Recognizing" the known faces
        # If the closest face's match status is 'True', it's a confirmed match.
        if matches[best_match_index]:
            person_name = f" {known_names[best_match_index]}"
            box_color = (0, 255, 0) # Green for trusted

        # If it's not a known face, set the flag so the alarm triggers
        else:
            intruder_detected = True

        # --- DRAWING ON THE FRAME ---
        # Draw the rectangle around the face
        cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
        
        # Draw the label with the name and distance (confidence level)
        label = f"{person_name} {confidence_label}"
        cv2.putText(frame, 
                    label, 
                    (left, top - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, # Font size
                    box_color, 
                    2) # Font thickness

    # --- ALARM LOGIC (THREAD SAFE) ---
    # Trigger the alarm if any detected face was labeled an intruder
    if intruder_detected:
        current_time = time.time()
        # Non-blocking alarm and cooldown timer
        if current_time - last_alarm_time > ALARM_COOLDOWN:
            # Create a separate, temporary thread to play the alarm sound
            threading.Thread(target=play_alarm, daemon=True).start()
            last_alarm_time = current_time

    # Display the final frame
    cv2.imshow("FACE SECURITY SYSTEM", frame)

    # Basic OpenCV shutdown command: Click the window and press 'q'
    if cv2.waitKey(1) & 0xFF == ord('e'):
        print("System shutting down...")
        break

# Graceful cleanup
cap.release()
cv2.destroyAllWindows()