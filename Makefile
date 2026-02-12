VERSION := 44
TYPE    := standard-virt

DEFS := $(PWD)/data/defs
REPO := $(PWD)/data/repo

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder \
		--force-data-dir=$(REPO) \
		build \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: list
list:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder \
		--force-data-dir=$(REPO) \
		list
