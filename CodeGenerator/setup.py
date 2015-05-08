import os, site, sys
from cx_Freeze import setup, Executable

## Get the site-package folder, not everybody will install
## Python into C:\PythonXX
site_dir = site.getsitepackages()[1]
include_dll_path = os.path.join(site_dir, "gnome")

## Collect the list of missing dll when cx_freeze builds the app
missing_dll = ['libffi-6.dll',
    'libgirepository-1.0-1.dll',
    'libgio-2.0-0.dll',
    'libgmodule-2.0-0.dll',
    'libglib-2.0-0.dll',
    'libintl-8.dll',
    'libgobject-2.0-0.dll',
    'libzzz.dll',
    'libwinpthread-1.dll',
    'libgtk-3-0.dll',
    'libgdk-3-0.dll',
    'libcairo-gobject-2.dll',
    'libfontconfig-1.dll',
    'libxmlxpat.dll',
    'libfreetype-6.dll',
    'libharfbuzz-gobject-0.dll',
    'libpng16-16.dll',
    'libgdk_pixbuf-2.0-0.dll',
    'libjpeg-8.dll',
    'libopenraw-7.dll',
    'librsvg-2-2.dll',
    'libpango-1.0-0.dll',
    'libpangocairo-1.0-0.dll',
    'libpangoft2-1.0-0.dll',
    'libpangowin32-1.0-0.dll',
    'libwebp-5.dll',
    'libatk-1.0-0.dll',
    'libtiff-5.dll',
    'libjasper-1.dll'
]

## We also need to add the glade folder, cx_freeze will walk
## into it and copy all the necessary files
glade_folder = 'glade'

## We need to add all the libraries too (for themes, etc..)
##gtk_libs = ['etc', 'lib', 'share']
## You can import only important Gtk Runtime data from the gtk folder
gtk_libs = ['lib\\gdk-pixbuf-2.0',
            'lib\\girepository-1.0',
            'share\\glib-2.0',
            'lib\\gtk-3.0']

## Create the list of includes as cx_freeze likes
include_files = []
for dll in missing_dll:
    include_files.append((os.path.join(include_dll_path, dll), dll))

## Let's add glade folder and files
include_files.append((glade_folder, glade_folder))

## Let's add gtk libraries folders and files
for lib in gtk_libs:
    include_files.append((os.path.join(include_dll_path, lib), lib))

base = None

## Lets not open the console while running the app
if sys.platform == "win32":
    base = "Win32GUI"

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "CodeGenerator",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]CodeGenerator.exe",   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                      # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )]

msi_data = {"Shortcut": shortcut_table}  # This will be part of the 'data' option of bdist_msi

#Change the default mis options
bdist_msi_options = {'data' : msi_data}

executables = [
    Executable("CodeGenerator.py",
               base=base,
               icon='toolbox.ico',
    )
]

buildOptions = dict(
    compressed = False,
    includes = ["gi", "csv", "datetime",],
    excludes = ["tkinter"],
    packages = ["gi"],
    include_files = include_files
    )

setup(
    name = "Code Generator",
    author = "Ed den Beer",
    version = "1.1",
    description = "Generating copy instructions for RsLogix5000 out of a list with tags in a CSV file",
    options = dict(build_exe = buildOptions, bdist_msi= bdist_msi_options ),
    executables = executables 
)
