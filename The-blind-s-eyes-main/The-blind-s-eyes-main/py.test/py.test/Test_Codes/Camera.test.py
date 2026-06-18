import cv2

# Make sure this matches your phone's IP
url = "http://192.168.1.15:8080/video" 

print("Connecting to the phone stream...")

cap = cv2.VideoCapture(url)

# --- THE MAGIC FIX FOR LAG ---
# This limits the waiting line to just 2 frames, throwing away old ones so you only see the live feed.
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2) 

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame.")
        break
        
    cv2.imshow("Smart Navigation - Live Stream", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Closing stream...")
        break

cap.release()
cv2.destroyAllWindows()