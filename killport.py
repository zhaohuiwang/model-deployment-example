
"""
This script check and kill occupied ports. THe port number(s) is passed as arguments

With a uv venv run this command

uv run python killport.py 8000              # one port
uv run python killport.py 8000 8001 8002    # multiple ports
"""

import os
import sys

import platform
import subprocess
import signal

def check_and_kill_port(port):
    system = platform.system()

    if system == "Windows":
        # Check if port is in use using netstat
        cmd = f'netstat -aon | findstr :{port}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout

        if str(port) in output:
            # Extract PID from netstat output
            for line in output.splitlines():
                if str(port) in line:
                    pid = line.split()[-1]
                    try:
                        print(f"Port {port} is in use by PID {pid}. Killing process...")
                        subprocess.run(f'taskkill /PID {pid} /F', shell=True, check=True)
                        print(f"Process with PID {pid} killed.")
                    except subprocess.CalledProcessError:
                        print(f"Failed to kill process with PID {pid}.")
                    return True
        else:
            print(f"Port {port} is not in use.")
            return False

    else:  # Unix-like systems (Linux/macOS)
        # Check if port is in use using lsof
        cmd = f'lsof -i :{port}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = result.stdout

        if len(output.splitlines()) > 1:  # First line is header
            # Extract PID from lsof output
            pid = output.splitlines()[1].split()[1]
            try:
                print(f"Port {port} is in use by PID {pid}. Killing process...")
                os.kill(int(pid), signal.SIGTERM)  # Send SIGTERM to terminate
                print(f"Process with PID {pid} killed.")
            except (OSError, ValueError) as e:
                print(f"Failed to kill process with PID {pid}: {e}")
            return True
        else:
            print(f"Port {port} is not in use.")
            return False

# Example usage
if __name__ == "__main__":
    for port in sys.argv:
        check_and_kill_port(port)