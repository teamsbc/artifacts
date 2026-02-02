
VERSION := 44
TYPE    := standard-virt

DATE := $(shell date -u +'%Y%m%d')
TAIL := 0
DEFS := $(PWD)/fedora/defs
DATA := $(PWD)/fedora/data

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder --force-data-dir=$(DATA) build --distro teamsbc-$(VERSION) $(TYPE)

.PHONY: compose
compose:
	@mkdir -p compose-$(DATE).$(TAIL)/
	@(cd compose-$(DATE).$(TAIL) && sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder --force-data-dir=$(DATA) build --seed=$(DATE) --with-buildlog --with-manifest --distro teamsbc-$(VERSION) standard-virt)
