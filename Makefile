VERSION := 44
TYPE    := standard-virt

DEFS := $(PWD)/fedora/defs
DATA := $(PWD)/fedora/data

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder \
		--force-data-dir=$(DATA) \
		build \
		--distro teamsbc-$(VERSION) $(TYPE)
