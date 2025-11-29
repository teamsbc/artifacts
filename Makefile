
VERSION := 44
TYPE    := standard-virt

DATE := $(shell date -u +'%Y%m%d')
DEFS := $(PWD)/fedora/defs
DATA := $(PWD)/fedora/data

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder --data-dir=$(DATA) build --distro teamsbc-$(VERSION) $(TYPE)

.PHONY: compose
compose:
	@mkdir -p compose-$(DATE)/
	@(cd compose-$(DATE) && sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder --data-dir=$(DATA) build --seed=$(DATE) --with-buildlog --with-manifest --distro teamsbc-$(VERSION) standard-virt)
