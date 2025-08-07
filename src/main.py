import mss
import numpy as np
import cv2 as cv
import json
import os
import torch
import time
import threading
import secrets
import win32gui
from ultralytics import YOLO
from pynput.mouse import Controller as mouse_controller, Button
from pynput.keyboard import KeyCode, Controller as kb_controller
from random import randint
from logger import logger
from pynput import keyboard


WINDOW_NAME = 'World of Warcraft'
MAX_WAIT_TIME = 22

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

def worker():
    global is_running
    logger.info("Worker started.")
    while is_running:
        with mss.mss() as sct:
            logger.info("Get active window to start fishing.")
            window = win32gui.GetForegroundWindow()
            left, top, right, bottom = win32gui.GetWindowRect(window)
            logger.info(f"Window position: ({left}, {top}), size: ({right - left}x{bottom - top})")
            frame_rect = win32gui.GetClientRect(window)
            client_left, client_top = win32gui.ClientToScreen(window, (0, 0))
            client_right = client_left + frame_rect[2]
            client_bottom = client_top + frame_rect[3]
            titlebar_height = client_top - top
            border_left = client_left - left
            border_right = right - client_right
            border_bottom = bottom - client_bottom
            logger.info(f"Titlebar height: {titlebar_height}")
            logger.info(f"Left border: {border_left}")
            logger.info(f"Right border: {border_right}")
            logger.info(f"Bottom border: {border_bottom}")
            window_game = {
                "top": top + titlebar_height,
                "left": left + border_left,
                "width": right - left - border_left - border_right,
                "height": bottom - top - titlebar_height - border_bottom,}
            try:
                while is_running:
                    logger.info("Start fishing...")
                    kb_click(KeyCode.from_char('\\'))
                    detect = False
                    start_time = time.time()
                    while is_running and not detect:
                        if time.time() - start_time > MAX_WAIT_TIME:
                            logger.error(f"No detection after {MAX_WAIT_TIME} seconds: try again.")
                            break
                        img = np.array(sct.grab(window_game))[:, :, :3]
                        results = model(img, verbose=False)
                        for box in results[0].boxes:
                            cls = int(box.cls[0])
                            conf = float(box.conf[0])
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            if cls == 0 and conf > 0.75:
                                detect = True
                                logger.info(f"Detected fish with {conf*100:.0f}% at [{x1}, {y1}, {x2}, {y2}]")
                                center_x = (x1 + x2) // 2 + border_left
                                center_y = (y1 + y2) // 2 + titlebar_height
                                mouse_click((center_x, center_y), Button.right)
                                sleep(733, 1234)
                        sleep(3, 13)
                    sleep(3, 13)
            except KeyboardInterrupt:
                pass

def window_get_active_rect():
  try:
    hwnd = win32gui.GetForegroundWindow()
    rect = win32gui.GetWindowRect(hwnd)
    # win32gui rect = (left, top, right, bot)
    # transform to (left, top, width, height)
    left = rect[0]
    top = rect[1]
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    if w < 256:
      w = 256
    if h < 128:
      h = 128
    out_rect = (left, top, w, h)
    return out_rect
  except:
    time.sleep(1)
    return (400, 400, 400, 400)


# State variable to track if started or stopped
is_running = False
thread_worker = None

def main():
    global is_running, thread_worker
    def on_press(key):
        global is_running, thread_worker
        if key == keyboard.Key.backspace:
            if not is_running:
                logger.info("Starting worker thread.")
                is_running = True
                thread_worker = threading.Thread(target=worker, daemon=True)
                thread_worker.start()
            else:
                logger.info("Stopping worker thread.")
                is_running = False
                if thread_worker is not None:
                    thread_worker.join()
                thread_worker = None
    with keyboard.Listener(on_press=on_press) as listener:
        logger.info("Press Backspace to start or stop fishing.")
        listener.join()

if __name__ == "__main__":
    main()
