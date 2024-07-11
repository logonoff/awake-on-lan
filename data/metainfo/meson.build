i18n = import('i18n')

metainfo_file = 'co.logonoff.summon.metainfo.xml.in'

appstream_file = i18n.merge_file(
        input: metainfo_file,
       output: 'co.logonoff.summon.metainfo.xml',
         type: 'xml',
       po_dir: meson.project_source_root() / 'po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

# Validate MetaInfo file
ascli_exe = find_program('appstreamcli', required: false)
if ascli_exe.found()
  test('validate metainfo file',
        ascli_exe,
        args: ['validate',
               '--no-net',
               '--pedantic',
               '--explain',
               metainfo_file],
        workdir: meson.current_source_dir()
  )
endif

appstream_src = gnome.compile_resources(
  'appstream-resources',
  'appstream.gresource.xml',
  c_name: 'appstream',
  source_dir: '.',
  dependencies: [appstream_file]
)
