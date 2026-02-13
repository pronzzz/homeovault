import PyInstaller.__main__
import os
import shutil

# Configuration
APP_NAME = "HomeoVault"
BACKEND_ENTRY = "backend/main.py"
FRONTEND_DIR = "frontend"
DATABASE_DIR = "database"

def build():
    print(f"Building {APP_NAME}...")

    # Ensure clean build
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # PyInstaller arguments
    args = [
        BACKEND_ENTRY,
        f"--name={APP_NAME}",
        "--onefile",
        "--clean",
        # Include Frontend files
        f"--add-data={FRONTEND_DIR}{os.pathsep}frontend",
        # Include Database directory (empty structure, not the db file itself usually, but here we want it)
        # We might want to handle DB creation on startup if missing, which we do.
        # But let's verify if we need to bundle anything else.
        # Hidden imports often needed for SQLModel/FastAPI/Uvicorn
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=sqlmodel",
        "--hidden-import=sqlite3",
    ]

    PyInstaller.__main__.run(args)
    print("Build Complete. Executable is in 'dist/' folder.")

if __name__ == "__main__":
    build()
