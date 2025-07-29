import threading
import time
import secrets
from pynput.mouse import Button, Controller
from flask import Flask, render_template_string, request, session, jsonify


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# State variable to track if started or stopped
is_running = False
click_thread = None

def click_loop():
    global is_running
    while is_running:
        click_at(100, 460)
        for _ in range(30):  # Check every 0.1s for stop, total 3s
            if not is_running:
                break
            time.sleep(0.1)

def click_at(x, y):
    mouse = Controller()
    mouse.position = (x, y)
    mouse.click(Button.left, 1)

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
    global is_running, click_thread
    data = request.get_json()
    running = data.get('running', False)
    if running and not is_running:
        is_running = True
        click_thread = threading.Thread(target=click_loop, daemon=True)
        click_thread.start()
    elif not running and is_running:
        is_running = False
    return jsonify(success=True, running=is_running)

# Run the app (use a different port if needed)
app.run(host="0.0.0.0", port=8081, debug=True, use_reloader=True)
