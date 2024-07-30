pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'awakeonlan'
gnome = import('gnome')

gnome.compile_resources('awakeonlan',
  'awakeonlan.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: [appstream_file]
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'awakeonlan.in',
  output: 'awakeonlan',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

awakeonlan_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'add_dialog.py',
  'wol_client.py',
  'settings_manager.py',
]

install_data(awakeonlan_sources, install_dir: moduledir)
