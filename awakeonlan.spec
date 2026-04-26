a = Analysis(
    ['src/awakeonlan.in'],
    datas=[
        ('src/awakeonlan.gresource', '.'),
        ('src/__init__.py', 'awakeonlan'),
        ('src/main.py', 'awakeonlan'),
        ('src/window.py', 'awakeonlan'),
        ('src/add_dialog.py', 'awakeonlan'),
        ('src/wol_client.py', 'awakeonlan'),
        ('src/settings_manager.py', 'awakeonlan'),
        ('data/co.logonoff.awakeonlan.gschema.xml', 'share/glib-2.0/schemas'),
        ('data/gschemas.compiled', 'share/glib-2.0/schemas'),
    ],
    hiddenimports=[
        'gi',
        'gi.repository.Gtk',
        'gi.repository.Adw',
        'gi.repository.Gio',
        'gi.repository.GLib',
        'gi.repository.GObject',
        'gi.repository.Pango',
        'gi.repository.GdkPixbuf',
        'gi.repository.Gdk',
        'gi.repository.Graphene',
        'awakeonlan',
        'awakeonlan.main',
        'awakeonlan.window',
        'awakeonlan.add_dialog',
        'awakeonlan.wol_client',
        'awakeonlan.settings_manager',
    ],
    hooksconfig={
        'gi': {
            'module-versions': {
                'Gtk': '4.0',
                'Adw': '1',
            },
            'themes': ['Adwaita'],
            'icons': ['Adwaita'],
        },
    },
    runtime_hooks=['_packaging/runtime_hook.py'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='awakeonlan',
    console=False,
    icon='awakeonlan.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='awakeonlan',
)
