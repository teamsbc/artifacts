VERSION := 45
TYPE    := standard-virt

DEFS := $(PWD)/data/defs
REPO := $(PWD)/data/repo

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamlplus image-builder \
		--force-repo-dir=$(REPO) \
		--force-defs-dir=$(DEFS) \
		build \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: manifest
manifest:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamlplus image-builder \
		--force-repo-dir=$(REPO) \
		--force-repo-dir=$(DEFS) \
		manifest \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: build-in-container
build-in-container:
	@sudo podman run --pull=newer \
		--privileged \
		-e IMAGE_BUILDER_EXPERIMENTAL=yamlplus \
		-v ${DEFS}:/defs \
		-v ${REPO}:/repo \
		-v .:/output:rw \
		ghcr.io/osbuild/image-builder-cli:latest \
		--force-repo-dir=/repo \
		--force-defs-dir=/defs \
		build \
		--output-dir /output \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: list
list:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamlplus image-builder \
		--force-repo-dir=$(REPO) \
		--force-defs-dir=$(DEFS) \
		list
