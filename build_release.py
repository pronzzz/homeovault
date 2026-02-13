import os
import subprocess
import shutil
import platform
import sys

def build():
    print("Building SimpleVault...")
    
    # 1. Install PyInstaller
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 2. Define data to include (Frontend)
    # On Windows: ; On Mac/Linux: :
    sep = ";" if platform.system() == "Windows" else ":"
    
    # We need to include the 'frontend' folder into the 'frontend' folder in the dist
    add_data = f"frontend{sep}frontend"
    
    # 3. run PyInstaller
    # --onefile: Create a single executable
    # --name: Name of the executable
    # --add-data: Include frontend files
    # --hidden-import: Ensure sqlmodel/fastapi dependencies are found
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SimpleVault",
        "--onefile",
        f"--add-data={add_data}",
        "--hidden-import=uvicorn",
        "--hidden-import=sqlmodel",
        "--hidden-import=sqlite3",
        "backend/main.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print("Build Complete.")
    print(f"Executable should be in 'dist/SimpleVault'")

if __name__ == "__main__":
    # Ensure we are in project root
    if not os.path.exists("backend/main.py"):
        print("Error: Run from project root 'SimpleVault/'")
    else:
        build()
