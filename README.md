👁️ Digital Eye: AI Navigation System

> Empowering Vision, Enhancing Life.> An Intelligent Agent Framework for Autonomous Spatial Awareness and Safety for the Visually Impaired.

 📌 Project Overview
**Digital Eye** is a real-time, multi-module AI navigation system designed to act as a "Rational Agent" for visually impaired individuals. By utilizing a standard smartphone camera linked to a processing unit, the system continuously monitors the environment, interprets spatial states, and executes rational actions (auditory guidance and alarms) to maximize user safety. 

This project goes beyond simple obstacle avoidance by integrating environmental context, depth estimation, and social awareness into a single continuous **Perceive → Think → Act** loop.

✨ Key Features
* **Real-Time Object Detection:** Utilizes dual YOLO models (Standard and Custom-trained) to identify everyday obstacles and hazards instantly.
* **Proximity Estimation:** Calculates distance dynamically without expensive LiDAR sensors by analyzing bounding box scaling.
* **Smart Facial Recognition:** Distinguishes between known individuals (friends/family) and strangers, providing an automatic intrusion alert system.
* **Rational Decision-Making (Audio Feedback):**
  * **Guidance Mode:** Calm, text-to-speech (TTS) descriptions of objects at a safe distance (> 100cm).
  * **Warning Mode:** Distinct beep for objects within the caution zone.
  * **Critical Alarm:** High-decibel siren for immediate hazards (< 27cm).
* **Network Resiliency:** Built-in auto-reconnect logic to handle unstable Wi-Fi or camera server drops seamlessly.
* **Optimized Performance:** Implements multi-threading for audio and frame-scaling hacks (400% faster face recognition) to maintain a lag-free real-time pipeline.

 🧠 AI Architecture
The system is built on the principles of an **Intelligent Rational Agent**:
1. **Perception:** Captures continuous visual states via IP Camera streams.
2. **Cognition (Data Fusion):** Merges YOLO classification data with Face Recognition encodings and estimated distances.
3. **Action:** Selects the optimal auditory response based on distance thresholds to minimize user cognitive load while maximizing safety.

 🛠️ Tech Stack
* **Language:** Python
* **Computer Vision:** OpenCV (`cv2`)
* **Deep Learning/AI:** Ultralytics (YOLOv8), `face_recognition` (dlib)
* **Concurrency:** `threading`, `queue`
* **Audio Processing:** `win32com.client` (SAPI.SpVoice), `winsound`

## 👥 Meet the Team
This project was developed by Information Systems Engineering students at **Helwan National University (HNU)**, under the supervision of **Dr. Samar Nour**.
* Philopateer
* Kirollos
* Maria
* Marina
* Youssef

---
*Developed with purpose. Engineered for impact.*
