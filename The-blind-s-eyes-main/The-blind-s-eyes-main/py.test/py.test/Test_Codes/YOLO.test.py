import cv2
from ultralytics import YOLO

print("1. Loading YOLOv8 Nano model...")
# This will automatically download the 'yolov8n.pt' file if you don't have it yet.
model = YOLO("yolov8n.pt") 

print("2. Model loaded! Running detection on a test image...")
# Ultralytics is smart enough to download and read an image directly from a URL!
test_image_url = "https://thumbs.dreamstime.com/b/cairo-street-scene-egypt-busy-street-scene-cairo-egypt-showing-people-crossing-road-motor-cycle-taxi-bus-behind-197141935.jpg?w=992"

# Feed the image to the model
results = model(test_image_url)

print("3. Detection complete! Drawing boxes...")
# Extract the image with the bounding boxes and labels drawn on it
annotated_frame = results[0].plot()

# Show the image on your screen
cv2.imshow("YOLO Static Test", annotated_frame)

print("SUCCESS! Press any key on your keyboard to close the window.")
# Wait indefinitely until you press a key, then close the window
cv2.waitKey(0)
v2.destroyAllWindows() 