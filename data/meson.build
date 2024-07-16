desktop_file = i18n.merge_file(
        input: 'co.logonoff.summon.desktop.in',
       output: 'co.logonoff.summon.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

test('Validate desktop file', desktop_utils, args: [desktop_file])

appstream_file = i18n.merge_file(
        input: 'co.logonoff.summon.metainfo.xml.in',
       output: 'co.logonoff.summon.metainfo.xml',
         type: 'xml',
       po_dir: meson.project_source_root() / 'po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

test('Validate appstream file',
    appstreamcli,
    args: ['validate', '--no-net', '--pedantic', '--explain', appstream_file],
    workdir: meson.current_source_dir()
)

install_data('co.logonoff.summon.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])

subdir('icons')

# glib_build_tools::compile_resources(
#   &["resources"],
#   "resources/resources.gresource.xml",
#   "dewduct.gresource",
# );

# resources = gnome.compile_resources('summon',
#   configure_file(
#     input : 'summon.gresource.xml.in',
#     output : 'summon.gresource.xml',
#     configuration: conf
#   ),
#   gresource_bundle: true,
#   install: true,
#   install_dir: pkgdatadir,
#   dependencies: [appstream_file, desktop_file],
#   source_dir: ['.', meson.current_source_dir()]
# )
