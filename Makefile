VERSION       := 46
TYPE          := lhotse-virt
IMAGE_VERSION := $(VERSION).$(shell date +%Y%m%d).0

DEFS := $(PWD)/data/defs
REPO := $(PWD)/data/repo

.PHONY: build
build:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamlplus,image-id=$(TYPE),image-version=$(IMAGE_VERSION) image-builder \
		--force-repo-dir=$(REPO) \
		--force-defs-dir=$(DEFS) \
		build \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: manifest
manifest:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamlplus,image-id=$(TYPE),image-version=$(IMAGE_VERSION) image-builder \
		--force-repo-dir=$(REPO) \
		--force-repo-dir=$(DEFS) \
		manifest \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: build-in-container
build-in-container:
	@sudo podman run --pull=newer \
		--privileged \
		--rm \
		-e IMAGE_BUILDER_EXPERIMENTAL=yamlplus,image-id=$(TYPE),image-version=$(IMAGE_VERSION) \
		-v ${DEFS}:/defs \
		-v ${REPO}:/repo \
		-v .:/output:rw \
		ghcr.io/osbuild/image-builder:latest \
		--force-repo-dir=/repo \
		--force-defs-dir=/defs \
		build \
		--output-dir /output \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: manifest-in-container
manifest-in-container:
	@sudo podman run --pull=newer \
		--privileged \
		--rm \
		-e IMAGE_BUILDER_EXPERIMENTAL=yamlplus,image-id=$(TYPE),image-version=$(IMAGE_VERSION) \
		-v ${DEFS}:/defs \
		-v ${REPO}:/repo \
		-v .:/output:rw \
		ghcr.io/osbuild/image-builder:latest \
		--force-repo-dir=/repo \
		--force-defs-dir=/defs \
		manifest --arch aarch64 \
		--distro teamsbc-$(VERSION) $(TYPE)

.PHONY: list
list:
	@sudo IMAGE_BUILDER_EXPERIMENTAL=yamlplus,image-id=$(TYPE),image-version=$(IMAGE_VERSION) image-builder \
		--force-repo-dir=$(REPO) \
		--force-defs-dir=$(DEFS) \
		list
