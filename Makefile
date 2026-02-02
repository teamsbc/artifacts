
VERSION := 44
TYPE    := standard-virt

DATE := $(shell date -u +'%Y%m%d')
TAIL := 0
LAST  = $(shell ls -d compose-$(VERSION)-$(DATE).* 2> /dev/null | sort -V | tail -n1)
DEFS := $(PWD)/fedora/defs
DATA := $(PWD)/fedora/data

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder \
		--force-data-dir=$(DATA) \
		build \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: compose-dir
compose-dir:
	@n=0; \
	while [ -d "compose-$(VERSION)-$(DATE).$$n" ]; do \
		n=$$((n+1)); \
	done; \
	path="compose-$(VERSION)-$(DATE).$$n"; \
	mkdir -p "$$path"

.PHONY: compose
compose: compose-dir
	@if [ -z "$(LAST)" ]; then echo "no path found!"; exit 1; fi
	@(cd $(LAST) && sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder \
		--force-data-dir=$(DATA) \
		build \
		--seed=$(DATE) \
		--with-buildlog \
		--with-manifest \
		--distro teamsbc-$(VERSION) standard-virt \
	)
