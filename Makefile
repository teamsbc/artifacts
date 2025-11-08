.PHONY: build

VERSION := 43
TYPE    := standard-virt

build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=./fedora/defs image-builder --data-dir=./fedora/data build --distro teamsbc-$(DISTRO) $(TYPE)
