> [!IMPORTANT]
> Issues for this repository are tracked at the [distribution bug tracker](https://github.com/teamsbc/distribution/issues).

# TeamSBC Definitions

This repository contains the [image-builder](https://osbuild.org/docs/developer-guide/projects/image-builder/) definitions for the various TeamSBC artifacts. Artifacts are also built here through the use of GitHub actions.

## Usage

For more information about how to use these artifacts and what they contain you can take a look at the [handbook](https://handbook.teamsbc.org/). Specifically the [installation section](https://handbook.teamsbc.org/getting-started/installation.html) or the [variants section](https://handbook.teamsbc.org/getting-started/variants.html).

## Downloads

Direct links to the latest builds of TeamSBC artifacts. Grouped by the Fedora version they are based on, and architecture. Named by the TeamSBC variant. You can also [browse artifacts](https://artifacts.teamsbc.net/index.html) on our artifacts storage.

### TeamSBC 44

#### x86_64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/44/x86_64/teamsbc-44-standard-virt-x86_64.raw.xz)

#### aarch64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/44/aarch64/teamsbc-44-standard-virt-aarch64.raw.xz)
- [standard-rpi4](https://artifacts.teamsbc.net/main/latest/44/aarch64/teamsbc-44-standard-rpi4-aarch64.raw.xz)
- [standard-rpi5](https://artifacts.teamsbc.net/main/latest/44/aarch64/teamsbc-44-standard-rpi5-aarch64.raw.xz)

### TeamSBC 45

#### x86_64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/45/x86_64/teamsbc-45-standard-virt-x86_64.raw.xz)

#### aarch64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/45/aarch64/teamsbc-45-standard-virt-aarch64.raw.xz)
- [standard-rpi4](https://artifacts.teamsbc.net/main/latest/45/aarch64/teamsbc-45-standard-rpi4-aarch64.raw.xz)
- [standard-rpi5](https://artifacts.teamsbc.net/main/latest/45/aarch64/teamsbc-45-standard-rpi5-aarch64.raw.xz)

## Building

You can build artifacts locally using the provided `Makefile` in this repository after you've installed the preqrequisites.

### Prerequisites

- `image-builder`

### Build

```
make build-in-container DISTRO=44 TYPE=standard-virt
```

Will build a TeamSBC Remix, Fedora 44 based `standard-virt` artifact. Since TeamSBC often uses the latest features of `image-builder` there's a chance that they might not yet be in a released version hence the default suggestion here is to build with the upstream container.

If you don't or can't use containers you can replace `build-in-container` with `build` and your locally installed `image-builder` version will be used.
