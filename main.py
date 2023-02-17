from pathlib import Path
from shutil import which
from subprocess import Popen
import threading
import time

from grade_dashboard import run as run_server

shutdown = threading.Event()


def run_view():
    node_js_runtime = which("pnpm") or which("yarn") or which("npm")
    view_path = Path(__file__).resolve().parent / "view"
    if node_js_runtime and view_path:
        p = Popen([node_js_runtime, "dev"], cwd=view_path)
        while p.poll() is None and not shutdown.is_set():
            stdout, stderr = p.communicate()
            if stdout:
                print(stdout.decode())
            if stderr:
                print(stderr.decode())
        if p.poll() is None:
            p.kill()
        print("View exited with code", p.returncode)


def main():
    view_thread = threading.Thread(target=run_view)
    server_thread = threading.Thread(target=run_server, args=(shutdown,))
    view_thread.start()
    server_thread.start()
    print("View, server threads started")

    try:
        while view_thread.is_alive() and server_thread.is_alive():
            view_thread.join(1)
            server_thread.join(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting...")

    shutdown.set()
    time.sleep(1)
    assert (
        not view_thread.is_alive() or not server_thread.is_alive()
    ), "Failed to shutdown server"
    print("View, server threads exited")


if __name__ == "__main__":
    main()
