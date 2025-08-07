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
from flask import Flask, render_template_string, request, jsonify
from random import randint
from logger import logger


WINDOW_NAME = 'World of Warcraft'
MAX_WAIT_TIME = 22

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

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

# State variable to track if started or stopped
is_running = False
thread_worker = None

def worker():
    global is_running
    logger.info("Worker started.")
    while is_running:
        with mss.mss() as sct:
            logger.info("Find and activate window to start fishing.")
            window = win32gui.FindWindow(None, WINDOW_NAME)
            print(window)
            if window:
                # Activate the window seems to not work from the web app
                win32gui.SetForegroundWindow(window)
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
            else:
                logger.error(f"Window '{WINDOW_NAME}' not found. Please start the game.")
                is_running = False
                break
            monitor = {
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
                        sleep(3, 13)
                    sleep(3, 13)
            except KeyboardInterrupt:
                pass


@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>flask-webapp</title>
            <link rel="icon" type="image/svg+xml" href="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg">
            <style>
                body {
                    background: #282a36;
                    color: #f8f8f2;
                    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }
                .drac-btn {
                    background: #8aff80;
                    color: #282a36;
                    border: none;
                    border-radius: 8px;
                    padding: 1em 2.5em;
                    font-size: 1.3em;
                    font-weight: 600;
                    box-shadow: 0 2px 12px #0003;
                    cursor: pointer;
                    transition: background 0.2s, color 0.2s, box-shadow 0.2s;
                    letter-spacing: 1px;
                    outline: none;
                }
                .drac-btn.stop {
                    background: #ff5555;
                    color: #f8f8f2;
                }
                .drac-btn:hover {
                    background: #bd93f9;
                    color: #f8f8f2;
                    box-shadow: 0 4px 20px #0005;
                }
                .drac-btn.stop:hover {
                    background: #ff79c6;
                    color: #282a36;
                }
                .drac-btn:active {
                    box-shadow: 0 1px 4px #0005;
                }
            </style>
        </head>
        <body>
            <button id="toggleBtn" class="drac-btn">Start</button>
            <script>
            let running = false;
            const btn = document.getElementById('toggleBtn');
            btn.onclick = async function() {
                running = !running;
                btn.textContent = running ? "Stop" : "Start";
                btn.classList.toggle("stop", running);
                await fetch('/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({running})
                });
            }
            </script>
        </body>
        </html>
    """)

@app.route('/toggle', methods=['POST'])
def toggle():
    global is_running, thread_worker
    data = request.get_json()
    running = data.get('running', False)
    if running and not is_running:
        is_running = True
        thread_worker = threading.Thread(target=worker, daemon=True)
        thread_worker.start()
    elif not running and is_running:
        is_running = False
    return jsonify(success=True, running=is_running)

# Run the app (use a different port if needed)
app.run(host="0.0.0.0", port=8081, debug=True, use_reloader=True)
