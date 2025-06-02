# build.py
"""
Build script to create executable using PyInstaller
"""

import os
import sys
import shutil
import PyInstaller.__main__


def build_executable():
    """Build the executable file"""

    # Clean previous builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # PyInstaller arguments
    args = [
        'main.py',
        '--name=EmployeeManagement',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',  # Add your icon file
        '--add-data=templates;templates',  # Include templates folder
        '--hidden-import=tkcalendar',
        '--hidden-import=babel.numbers',
        '--collect-data=tkcalendar',
        '--collect-data=babel',
        '--clean',
        '--noconfirm',
    ]

    # Add platform-specific options
    if sys.platform == 'win32':
        args.extend([
            '--version-file=version_info.txt',  # Windows version info
        ])

    print("Building executable...")
    PyInstaller.__main__.run(args)

    # Create distribution folder
    dist_folder = 'EmployeeManagement_v1.0.0'
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    os.makedirs(dist_folder)

    # Copy executable
    if sys.platform == 'win32':
        shutil.copy2('dist/EmployeeManagement.exe', dist_folder)
    else:
        shutil.copy2('dist/EmployeeManagement', dist_folder)

    # Copy additional files
    for folder in ['templates', 'documents', 'exports']:
        os.makedirs(os.path.join(dist_folder, folder), exist_ok=True)

    # Create README for distribution
    with open(os.path.join(dist_folder, 'README.txt'), 'w') as f:
        f.write("""Employee Management System v1.0.0
================================

Installation:
1. Extract all files to a folder of your choice
2. Run EmployeeManagement.exe

First Run:
- The system will create a database file automatically
- Default admin credentials: admin/admin (change immediately)

Folders:
- templates/ - Document templates
- documents/ - Generated documents
- exports/ - Exported data

Support:
Email: support@yourcompany.com
""")

    print(f"Build complete! Distribution folder: {dist_folder}")


if __name__ == "__main__":
    build_executable()