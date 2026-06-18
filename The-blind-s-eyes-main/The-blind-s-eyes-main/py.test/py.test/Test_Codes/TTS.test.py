import cv2
from ultralytics import YOLO
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print(text)
    engine.say(text)
    engine.runAndWait()

model = YOLO("yolov8n.pt")

test_image_url = "https://thumbs.dreamstime.com/b/cairo-street-scene-egypt-busy-street-scene-cairo-egypt-showing-people-crossing-road-motor-cycle-taxi-bus-behind-197141935.jpg?w=992"

results = model(test_image_url)

names = model.names
detected_objects = set()

for box in results[0].boxes:
    class_id = int(box.cls[0])
    label = names[class_id]
    detected_objects.add(label)

if detected_objects:
    text = "I detected " + ", ".join(detected_objects)
else:
    text = "I did not detect any objects"

speak(text)

annotated_frame = results[0].plot()
cv2.imshow("YOLO + TTS Test", annotated_frame)

cv2.waitKey(0)
cv2.destroyAllWindows()