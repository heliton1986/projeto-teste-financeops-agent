import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    ui_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "ui", "app.py")
    subprocess.run(["streamlit", "run", ui_path], check=True)
