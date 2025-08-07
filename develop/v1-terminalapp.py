import mss
import numpy as np
import cv2 as cv
import json
import os
import torch
import time
from ultralytics import YOLO
from pynput.mouse import Controller as mouse_controller, Button
from pynput.keyboard import KeyCode, Controller as kb_controller
from random import randint
from logger import logger

MAX_WAIT_TIME = 20

# Check if ROCm-compatible GPU is available
logger.info(f"PyTorch version: {torch.__version__}")
logger.info(f"GPU available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"Device count: {torch.cuda.device_count()}")
    logger.info(f"Current device index: {torch.cuda.current_device()}")
    logger.info(f"Device name: {torch.cuda.get_device_name(0)}")
    logger.info(f"Device capability: {torch.cuda.get_device_capability(0)}")
else:
    logger.warning(f"No compatible GPU detected use CPU.")

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
  sleep(344, 773)
  mouse.click(button)
  sleep(51, 99)

def kb_click(key):
  kb.press(key)
  sleep(9, 23)
  kb.release(key)

with mss.mss() as sct:
    logger.info("Setup monitor and screen for fishing automation.")
    window = sct.monitors[0]
    monitor = {"top": 26, "left": 1, "width": 958, "height": 664}
    try:
        while True:
            logger.info("Start fishing...")
            kb_click(KeyCode.from_char('\\'))
            detect = False
            start_time = time.time()
            while not detect:
                if time.time() - start_time > MAX_WAIT_TIME:
                    logger.error(f"No detection after {MAX_WAIT_TIME} seconds: try again.")
                    break
                img = np.array(sct.grab(monitor))[:, :, :3]
                results = model(img, verbose=False)
                for box in results[0].boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    if cls == 0 and conf > 0.75:
                        detect = True
                        logger.info(f"Detected fish with {conf*100:.0f}% at [{x1}, {y1}, {x2}, {y2}]")
                        center_x = (x1 + x2) // 2 + 1
                        center_y = (y1 + y2) // 2 + 26
                        mouse_click((center_x, center_y), Button.right)
                        sleep(733, 1234)
            # DEBUG: uncomment to visualize detection
            # cv.imshow("Detection", results[0].plot())
            # if cv.waitKey(1) == ord('q'):
            #     cv.destroyAllWindows()
            #     break
            
    except KeyboardInterrupt:
        pass
