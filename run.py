import subprocess

while True:
    """However, you should be careful with the '.wait()'"""
    p = subprocess.Popen(['python3.6', 'main.py']).wait()
