import subprocess
import webbrowser
import time
import socket
import sys


def find_free_port(start_port=8000, end_port=8100):
    """Finds an available port in a given range."""
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports available in range.")


def run_server():
    port = find_free_port()
    url = f"http://127.0.0.1:{port}/"
    print(f"✅ Starting server at: {url}")

    # Start uvicorn server
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "Apps.app:app",
            "--reload",
            "--port",
            str(port),
        ]
    )

    # Give server a moment to start
    time.sleep(2)

    # Open browser
    webbrowser.open(url)

    # Keep the process running
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        process.terminate()


if __name__ == "__main__":
    run_server()
