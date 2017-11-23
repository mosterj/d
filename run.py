import subprocess

while True:
    p = subprocess.Popen(['python3.6', 'main.py']).wait()
