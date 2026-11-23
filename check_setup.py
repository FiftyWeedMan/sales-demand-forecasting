# check_setup.py
# Step 1: Check which libraries are installed and create project folders.

import sys
import os
import importlib

print("Python version:", sys.version.split()[0])
print()

# The 4 libraries our project needs (name used in 'import')
libraries = ["pandas", "sklearn", "matplotlib", "streamlit"]

missing = []
for lib in libraries:
    try:
        module = importlib.import_module(lib)      # try to import it
        print(f"[OK]      {lib:<12} version {module.__version__}")
    except ImportError:
        print(f"[MISSING] {lib}")
        missing.append(lib)

# sqlite3 is built into Python, so it should always be there
import sqlite3
print(f"[OK]      {'sqlite3':<12} built-in (SQLite version {sqlite3.sqlite_version})")

# Create the folders we will use
for folder in ["data", "charts"]:
    os.makedirs(folder, exist_ok=True)      # exist_ok = no error if it already exists
print("\nFolders ready: data/  charts/")

if missing:
    # pip uses 'scikit-learn' as the install name for 'sklearn'
    names = ["scikit-learn" if m == "sklearn" else m for m in missing]
    print("\nTo install the missing ones, run:")
    print("    pip install " + " ".join(names))
else:
    print("\nEverything is installed. Ready for Step 2!")
