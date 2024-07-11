summon_sources = [
  'main.c',
  'summon-application.c',
  'summon-window.c',
]

summon_deps = [
  dependency('gtk4'),
  dependency('libadwaita-1', version: '>= 1.4'),
]

summon_sources += gnome.compile_resources('summon-resources',
  'summon.gresource.xml',
  c_name: 'summon'
)

executable(
  'summon',
  appstream_src,
  summon_sources,
  dependencies: summon_deps,
       install: true,
)
