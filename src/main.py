import mss
import numpy as np
import cv2 as cv
import json
import os
import torch
from ultralytics import YOLO
from pynput.mouse import Controller as mouse_controller, Button
from pynput.keyboard import Key, KeyCode, Controller as kb_controller, Listener as kb_listener
import time
from random import randint

print("PyTorch version:", torch.__version__)

# Check if ROCm-compatible GPU is available
print("GPU available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("Device count:", torch.cuda.device_count())
    print("Current device index:", torch.cuda.current_device())
    print("Device name:", torch.cuda.get_device_name(0))
    print("Device capability:", torch.cuda.get_device_capability(0))
else:
    print("No compatible GPU detected.")

with open("config.json", "r") as f:
    config = json.load(f)
os.chdir(config["workdir"])

model = YOLO("models/yolo11s-wow-fishing-classic.pt")
model.to("cuda" if torch.cuda.is_available() else "cpu")

mouse = mouse_controller()
kb = kb_controller()

def sleep(min, max):
  time.sleep(randint(min, max)/1000)

def mouse_click(pos, button):
  mouse.position = pos
  sleep(344, 573)
  mouse.click(button)
  sleep(51, 79)

def kb_click(key):
  kb.press(key)
  sleep(3, 17)
  kb.release(key)

with mss.mss() as sct:
    window = sct.monitors[0]
    monitor = {"top": 26, "left": 1, "width": 958, "height": 664}
    try:
        while True:
            kb_click(KeyCode.from_char('\\'))
            detect = False
            start_time = time.time()
            while not detect:
                if time.time() - start_time > 28:
                    print("No detection after 28 seconds: try again.")
                    break
                img = np.array(sct.grab(monitor))[:, :, :3]
                results = model(img)
                for box in results[0].boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    if cls == 0 and conf > 0.70:
                        detect = True
                        print(f"Detected class {cls} with confidence {conf:.2f} at [{x1}, {y1}, {x2}, {y2}]")
                        center_x = (x1 + x2) // 2 + 1
                        center_y = (y1 + y2) // 2 + 26
                        print((center_x, center_y))
                        mouse_click((center_x, center_y), Button.right)
                        sleep(733, 1234)
            # cv.imshow("Detection", results[0].plot())
            # if cv.waitKey(1) == ord('q'):
            #     cv.destroyAllWindows()
            #     break
            
    except KeyboardInterrupt:
        pass
