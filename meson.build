project('summon', 'rust',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')

appstreamcli = find_program('appstreamcli', required: true, disabler: true)
cargo_bin = find_program('cargo', required: true)
compile_schemas = find_program('glib-compile-schemas', required: true, disabler: true)
desktop_utils = find_program('desktop-file-validate', required: true)
glib_compile_resources = find_program('glib-compile-resources', required: true)

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

conf = configuration_data()
conf.set_quoted('VERSION', meson.project_version())
conf.set_quoted('GETTEXT_PACKAGE', 'summon')
conf.set_quoted('LOCALEDIR', get_option('prefix') / get_option('localedir'))
conf.set_quoted('PKGDATADIR', pkgdatadir)


subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
