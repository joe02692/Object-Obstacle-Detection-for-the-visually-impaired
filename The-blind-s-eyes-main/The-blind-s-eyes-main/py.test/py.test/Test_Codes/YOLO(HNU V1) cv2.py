import cv2
from ultralytics import YOLO

def main():
    # 1. Load your newly trained custom brain
    # Using the exact absolute path to avoid the VS Code folder error
    print("Loading custom model...")
    model = YOLO(r"c:\Users\joeel\py.test\best.pt")

    # 2. Set the path to the picture you downloaded
    image_path = r"C:\Users\joeel\Downloads\Fan_IMG.jpg"

    # 3. Run the AI detection on the image
    print("Running detection...")
    results = model(image_path)

    # 4. YOLO has a built-in .plot() function that automatically 
    # draws the colored boxes and labels for us on static images
    annotated_frame = results[0].plot()

    # 5. Display the image on your screen
    cv2.imshow("Custom AI Fan Test", annotated_frame)
    
    print("Success! Press any key on your keyboard to close the image.")
    
    # Wait infinitely until you press any key to close the window
    cv2.waitKey(0) 
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()