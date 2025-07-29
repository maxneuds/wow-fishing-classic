import threading
from pynput.mouse import Button, Controller
from flask import Flask, render_template_string, request

def click_at(x, y):
    mouse = Controller()
    mouse.position = (x, y)
    mouse.click(Button.left, 1)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
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
            form {
                background: #44475a;
                padding: 2em 2.5em;
                border-radius: 12px;
                box-shadow: 0 4px 24px #0004;
                display: flex;
                flex-direction: column;
                gap: 1em;
                min-width: 320px;
            }
            input[type="number"] {
                background: #282a36;
                color: #f8f8f2;
                border: 1px solid #6272a4;
                border-radius: 6px;
                padding: 0.5em;
                font-size: 1em;
                outline: none;
                transition: border 0.2s;
            }
            input[type="number"]:focus {
                border: 1.5px solid #bd93f9;
            }
            button {
                background: #50fa7b;
                color: #282a36;
                border: none;
                border-radius: 6px;
                padding: 0.7em 1.2em;
                font-size: 1.1em;
                font-weight: 500;
                box-shadow: 0 2px 8px #0002;
                cursor: pointer;
                transition: background 0.2s, box-shadow 0.2s;
                letter-spacing: 0.5px;
            }
            button:hover {
                background: #8be9fd;
                color: #282a36;
                box-shadow: 0 4px 16px #0003;
            }
            #result {
                margin-top: 1.5em;
                font-size: 1.1em;
                color: #bd93f9;
                text-align: center;
            }
        </style>
        <form id="clickForm">
            <label>X: <input type="number" name="x" value="100" required></label>
            <label>Y: <input type="number" name="y" value="460" required></label>
            <button type="submit">Trigger Click</button>
        </form>
        <div id="result"></div>
        <script>
        document.getElementById('clickForm').onsubmit = async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const response = await fetch('/click', {
                method: 'POST',
                body: formData
            });
            const text = await response.text();
            document.getElementById('result').innerHTML = text;
        }
        </script>
    """)

@app.route('/click', methods=['POST'])
def trigger_click():
    x = int(request.form['x'])
    y = int(request.form['y'])
    threading.Thread(target=click_at, args=(x, y)).start()
    return "Click triggered! <a href='/'>Back</a>"

# Run the app (use a different port if needed)
app.run(port=8081, debug=True, use_reloader=True)
