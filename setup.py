from cx_Freeze import setup, Executable
import sys
import os

base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Path to the DLLs
vcruntime_dll = os.path.join(os.environ['SystemRoot'], 'System32', 'vcruntime140.dll')
msvcp_dll = os.path.join(os.environ['SystemRoot'], 'System32', 'msvcp140.dll')

executables = [Executable("main.py", base=base, target_name="EVM-120.exe")]

# Include additional files (e.g., images and DLLs)
include_files = ["speed_0.gif", "speed_40.gif", "speed_80.gif", "speed_high.gif", vcruntime_dll, msvcp_dll]

options = {
    "build_exe": {
        "packages": ["requests", "PyQt5"],
        "includes": [],
        "include_files": include_files,
        "excludes": [],
    },
    "bdist_msi": {
        "upgrade_code": "{778a4d35-a00d-41fa-adde-1aab47e041ae}",  # Replace with your GUID
        "add_to_path": True,
        "initial_target_dir": r"[ProgramFilesFolder]\EVM-120",
    }
}

setup(
    name="EVM-120",
    version="1.0",
    description="SimRail EVM-120 segéd app",
    options=options,
    executables=executables,
)
