import eventlet
eventlet.monkey_patch()

import time
import psutil
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-devops'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

boot_time = psutil.boot_time()

def background_thread():
    while True:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        uptime_seconds = int(time.time() - boot_time)
        
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s" if days > 0 else f"{hours}h {minutes}m {seconds}s"
        
        socketio.emit('system_metrics', {
            'cpu': cpu,
            'ram': ram,
            'uptime': uptime_str
        })
        socketio.sleep(1)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.start_background_task(target=background_thread)
    socketio.run(app, host="0.0.0.0", port=5000)
