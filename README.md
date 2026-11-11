> [!IMPORTANT]
> Issues for this repository are tracked at the [distribution bug tracker](https://github.com/teamsbc/distribution/issues).

# TeamSBC Definitions

This repository contains the [image-builder](https://osbuild.org/docs/developer-guide/projects/image-builder/) definitions and GitHub Actions workflows for TeamSBC images, update payloads, and system extensions.

## Usage

For more information about how to use these artifacts and what they contain you can take a look at the [handbook](https://handbook.teamsbc.org/). Specifically the [installation section](https://handbook.teamsbc.org/getting-started/installation.html) or the [variants section](https://handbook.teamsbc.org/getting-started/variants.html).

## Downloads

Browse published images by Fedora version, architecture, and image type in the [artifact storage](https://artifacts.teamsbc.net/index.html).

### TeamSBC 46

#### x86_64

- [makalu-virt](https://artifacts.teamsbc.net/main/46/x86_64/teamsbc-makalu-virt/index.html)

#### aarch64

- [makalu-virt](https://artifacts.teamsbc.net/main/46/aarch64/teamsbc-makalu-virt/index.html)
- [makalu-rpi4](https://artifacts.teamsbc.net/main/46/aarch64/teamsbc-makalu-rpi4/index.html)
- [makalu-rpi5](https://artifacts.teamsbc.net/main/46/aarch64/teamsbc-makalu-rpi5/index.html)

Makalu update payloads and system extensions are published separately in the [updates](https://updates.teamsbc.net/index.html) and [extensions](https://extensions.teamsbc.net/index.html) storage.

## Building

The `Makefile` provides local and container-based image builds. The definitions are in `data/defs`, and the build-time package repositories are in `data/repo`.

### Prerequisites

- GNU Make and `sudo`
- Podman for container builds, or a compatible `image-builder` installed locally for local builds

### Build

```sh
make build-in-container VERSION=46 TYPE=makalu-virt
```

This builds a Fedora 46-based `makalu-virt` image using the latest upstream image-builder container and writes the output to the current directory. The container runs with elevated privileges. TeamSBC often uses image-builder features that may not yet be available in a release.

Use `make build VERSION=46 TYPE=makalu-virt` to build with the locally installed image-builder. The CI workflow requests extras explicitly and publishes the `/usr` partition, UKI, and system extensions separately.
