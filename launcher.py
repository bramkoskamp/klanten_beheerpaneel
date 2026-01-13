import threading
import time
import webbrowser
from app import app

def run_flask():
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

    # Houd exe actief
    while True:
        time.sleep(1)
