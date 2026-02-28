VERSION := 45
TYPE    := standard-virt

DEFS := $(PWD)/data/defs
REPO := $(PWD)/data/repo

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder \
		--force-repo-dir=$(REPO) \
		build \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: build-in-container
build-in-container:
	@sudo podman run --pull=newer \
		--privileged \
		-e IMAGE_BUILDER_EXPERIMENTAL=yamldir=/defs \
		-v ${DEFS}:/defs \
		-v ${REPO}:/repo \
		-v .:/output:rw \
		ghcr.io/osbuild/image-builder-cli:latest \
		--force-repo-dir=/repo \
		build \
		--output-dir /output \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: list
list:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamldir=$(DEFS) image-builder \
		--force-repo-dir=$(REPO) \
		list
