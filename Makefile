.PHONY: all test clean build

# these are debug scripts and not meant to be published on Flathub

# Application ID for the Flatpak package
APP_ID = co.logonoff.awakeonlan

# Command to run the Flatpak builder
# BUILDER = flatpak run --command=flatpak-builder --socket=gpg-agent org.flatpak.Builder
BUILDER = flatpak-builder --install-deps-from=flathub

# Command to run the Flatpak builder linter
BUILDER_LINT = flatpak run --command=flatpak-builder-lint org.flatpak.Builder

# Directory where the Flatpak package is built
BUILDDIR = $(shell pwd)/build

build:
	$(BUILDER) --user --install --force-clean --sandbox --ccache --mirror-screenshots-url=https://dl.flathub.org/media/ --repo=repo $(BUILDDIR) $(APP_ID).yml

lint:
	$(BUILDER_LINT) manifest $(APP_ID).yml
	$(BUILDER_LINT) repo repo

# keeps the data when the app is uninstalled
clean:
	rm -rf repo
	rm -rf build
	rm -rf manifest
	flatpak uninstall $(APP_ID) -y

reset: clean
	rm -rf .flatpak-builder

run:
	flatpak run $(APP_ID)

i18n:
	xgettext --files-from=po/POTFILES --from-code=UTF-8 --output po/awakeonlan.pot --copyright-holder="logonoff" --package-name="$(APP_ID)"
	# pushd po && msginit --locale=en --input=awakeonlan.pot && popd
