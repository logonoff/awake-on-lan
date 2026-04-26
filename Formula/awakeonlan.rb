class Awakeonlan < Formula
  desc "Simple libadwaita-based Wake on LAN application for waking computers remotely"
  homepage "https://github.com/logonoff/awake-on-lan"
  version "0.5.2"
  url "https://github.com/logonoff/awake-on-lan/releases/download/#{version}/awakeonlan-#{version}.tar.xz"
  sha256 "ff7bbc4fcbfe0d0db180ae247f4ca1d8c5e69ab143f3d9dd47e0b56b477bb8c2"
  license "GPL-3.0-or-later"

  depends_on "desktop-file-utils" => :build
  depends_on "gettext" => :build
  depends_on "meson" => :build
  depends_on "ninja" => :build
  depends_on "pkgconf" => :build

  depends_on "adwaita-icon-theme"
  depends_on "glib"
  depends_on "gtk4"
  depends_on "libadwaita"
  depends_on "pygobject3"
  depends_on "python@3.13"

  on_macos do
    depends_on "gettext"
  end

  def install
    system "meson", "setup", "build", *std_meson_args
    system "meson", "compile", "-C", "build", "--verbose"
    system "meson", "install", "-C", "build"
    rm share/"glib-2.0/schemas/gschemas.compiled"
  end

  def post_install
    system Formula["glib"].opt_bin/"glib-compile-schemas", HOMEBREW_PREFIX/"share/glib-2.0/schemas"
    system Formula["gtk4"].opt_bin/"gtk4-update-icon-cache", "-f", "-t", HOMEBREW_PREFIX/"share/icons/hicolor"
  end

  test do
    assert_predicate bin/"awakeonlan", :executable?
  end
end
