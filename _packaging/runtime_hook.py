import os
import sys

if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    internal = os.path.join(exe_dir, '_internal')
    os.environ['GSETTINGS_SCHEMA_DIR'] = os.path.join(exe_dir, 'share', 'glib-2.0', 'schemas')
    os.environ['XDG_DATA_DIRS'] = os.pathsep.join([
        os.path.join(exe_dir, 'share'),
        os.path.join(internal, 'share'),
    ])
    os.environ['GSK_RENDERER'] = 'cairo'
